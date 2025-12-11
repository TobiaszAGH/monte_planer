from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QToolTip
from PyQt5.QtGui import QPen
from PyQt5.QtCore import QPoint, Qt
from widgets.lesson_block import LessonBlock
from functions import snap_position


class MyView(QGraphicsView):

    def __init__(self,parent):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.db = parent.db
        self.classes = []
        self.mode = ''
        self.widths = [0]
        self.block_start = -1
        self.new_block = False
        self.setMouseTracking(True)


        self.top_bar_h = 75
        self.left_bar_w = 50
        self.update_size_params()

    def set_classes(self, classes):
        self.widths = [0]
        self.classes = classes
        last_cls = classes[0].get_class()
        for cls in classes:
            if cls.get_class() != last_cls:
                self.widths.append(0)
                last_cls = cls.get_class()
            self.widths[-1]+=1
        self.class_names = [c.full_name() for c in classes]
        self.update_column_sizes()
            

    def update_column_sizes(self):
        l = len(self.classes)
        self.block_w = self.day_w/l if l>0 else self.day_w
        self.boundries = [0]
        for width in self.widths:
            self.boundries.append(self.block_w*width+self.boundries[-1])

    def update_size_params(self):
        self.scene_width = self.geometry().width()-10
        self.scene_height = self.geometry().height()-10
        self.hour_h = (self.scene_height-self.top_bar_h)/8
        self.five_min_h = self.hour_h/12
        self.day_w = (self.scene_width-self.left_bar_w)/5
        self.update_column_sizes()


    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)

        self.update_size_params()
        self.draw_frame()

    def set_mode_new(self):
        self.mode = 'new'
    
    def mousePressEvent(self, event):
        if self.mode == 'new':
            if event.button() == Qt.MouseButton.LeftButton:
                l = len(self.class_names)
                if l == 0:
                    return False
                self.block_start = self.how_many_5_min_blocks(event)
                self.new_block_top = snap_position(event.y(), self.five_min_h, self.top_bar_h)
                self.new_block_left = snap_position(event.x(), self.block_w, self.left_bar_w)
                self.new_block = LessonBlock(self.new_block_left, self.new_block_top, self.block_w, self.five_min_h)
                self.scene().addItem(self.new_block)
            elif event.button() == Qt.MouseButton.RightButton:
                self.drop_new_block()


    def mouseReleaseEvent(self, event):
        self.block_start = -1
        self.new_block = False

    def display_hour(self, mins):
        hs = int(mins//12+8)
        mins = int(mins%12)*5
        return f'{hs}:{mins:02d}' 
    
    def how_many_5_min_blocks(self, event):
        y = event.y() - self.top_bar_h
        mins = y//self.five_min_h
        return mins

    def drop_new_block(self):
        if self.new_block:
            self.scene().removeItem(self.new_block)
        self.new_block = False
        self.block_start = -1
        QToolTip.showText(QPoint(), '')

    def mouseMoveEvent(self, event=0):
        if self.mode == 'new':
            # stop if moved out of bounds:
            if (event.y() < self.top_bar_h or event.x() < self.left_bar_w):
                self.drop_new_block()
                return
            
            # show tooltip
            now = self.how_many_5_min_blocks(event)
            times = [now, self.block_start] if self.block_start >=0 else [now]
            times.sort()
            msg = '-'.join([self.display_hour(t) for t in times])
            if self.block_start>=0:
                msg += f' ({int(abs(now-self.block_start)*5)})'
            QToolTip.showText(event.globalPos(), msg)

            # update block
            if self.new_block:
                cursor_x = snap_position(event.x(), self.block_w, self.left_bar_w)
                x, width = self.calculate_x_w(cursor_x)
                
                new_block_bottom = snap_position(event.y(), self.five_min_h, self.top_bar_h)
                height = abs(new_block_bottom - self.new_block_top)
                y = min(new_block_bottom, self.new_block_top)
                self.new_block.setRect(x, y, width, height)


    def calculate_x_w(self, cursor_x):
        # if in the same subclass block dont stretch
        if self.new_block_left==cursor_x:
            return self.new_block_left, self.block_w

        # get the bottom boundry
        x1 = (self.new_block_left - self.left_bar_w)%self.day_w
        for boundry in self.boundries:
            if x1>=boundry:
                bottom = boundry
        
        day_start = snap_position(self.new_block_left, self.day_w, self.left_bar_w)
        x = bottom+day_start
        top = self.boundries[self.boundries.index(bottom)+1]
        w = top-bottom
        return x,w


    def draw_frame(self):
        scene = self.scene()
        scene.clear()
        scene.setSceneRect(0,0, self.scene_width, self.scene_height)

        wide_pen = QPen()
        wide_pen.setWidth(2)
        line = scene.addLine(0, self.top_bar_h, self.scene_width, self.top_bar_h)
        line.setPen(wide_pen)
        line = scene.addLine(0, 0, self.scene_width, 0)
        line.setPen(wide_pen)
        line = scene.addLine(0, 0, 0, self.scene_height)
        line.setPen(wide_pen)
        line = scene.addLine(0, self.scene_height, self.scene_width, self.scene_height)
        line.setPen(wide_pen)
        line = scene.addLine(self.left_bar_w, 0, self.left_bar_w, self.scene_height)
        line.setPen(wide_pen)

        for hour in range(8,16):
            pos = self.top_bar_h+(hour - 7)*self.hour_h
            text = scene.addSimpleText(f'{hour}-{hour+1}')

            # center text
            text_x = (self.left_bar_w-text.boundingRect().width())/2
            text_y = pos-(self.hour_h+text.boundingRect().height())/2
            text.setPos(text_x, text_y)

            scene.addLine(0, pos, self.left_bar_w, pos)

        l = len(self.classes)
        days = 'Poniedziałek Wtorek Środa Czwartek Piątek'.split()
        for day in range(5):
            pos = self.day_w*(day+1)+self.left_bar_w
            line = scene.addLine(pos, 0, pos, self.scene_height)
            line.setPen(wide_pen)
            
            text = scene.addSimpleText(days[day])
            text_x = pos - (self.day_w + text.boundingRect().width())/2
            text_y = (self.top_bar_h/2 - text.boundingRect().height())/2
            text.setPos(text_x, text_y)
        if l>0:
            scene.addLine(self.left_bar_w, self.top_bar_h/2, self.scene_width, self.top_bar_h/2)
            self.block_w = self.day_w/l
            for i in range(5):
                for n, class_name in enumerate(self.class_names):
                    pos = self.block_w*(n+i*l+1)+self.left_bar_w
                    text = scene.addSimpleText(class_name)
                    text_x = pos - (text.boundingRect().width()+self.block_w)/2
                    text_y = self.top_bar_h/2 + (self.top_bar_h/2 - text.boundingRect().height())/2
                    text.setPos(text_x, text_y)
                    scene.addLine(pos, self.top_bar_h/2, pos, self.scene_height)

            # print(self.data['blocks'].keys())
            # for n, class_name in enumerate(self.class_names):
            #     for block in self.data['blocks'][class_name]:
            #         x = left_bar_w + day_w*block['day'] + n*block_w
            #         y = five_min_h*block['start'] + top_bar_h
                    
            #         block_h = five_min_h* block['duration']
            #         rect = scene.addRect(x, y, block_w, block_h)
            #         # rect.setPen(wide_pen)
            #         # rect.setZValue(200)
            #         brush = QBrush(Qt.lightGray)
            #         rect.setBrush(brush)
            #         # print(rect)


        

