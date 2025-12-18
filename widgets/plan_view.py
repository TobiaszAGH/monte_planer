from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QToolTip, QGraphicsTextItem
from PyQt5.QtGui import QPen
from PyQt5.QtCore import QPoint, Qt
from widgets.lesson_block import LessonBlock
from functions import snap_position, display_hour
from data import Data, Class, Subclass


class MyView(QGraphicsView):

    def __init__(self,parent):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.db: Data = parent.db
        self.classes = []
        self.blocks = []
        self.mode = 'normal'
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
    def set_mode(self, mode):
        self.mode = mode
        for block in self.scene().items():
            if isinstance(block, LessonBlock):
                block.set_movable(mode=='move', self.five_min_h, self.top_bar_h)
                block.set_selectable(mode!='new')
                
    
    def mousePressEvent(self, event):

        if self.mode == 'new':
            if event.button() == Qt.MouseButton.LeftButton:
                l = len(self.class_names)
                if l == 0:
                    return False
                self.block_start = self.how_many_5_min_blocks(event)
                self.new_block_top = snap_position(event.y(), self.five_min_h, self.top_bar_h)
                self.new_block_left = snap_position(event.x(), self.block_w, self.left_bar_w)
                self.new_block = LessonBlock(self.new_block_left, self.new_block_top, self.block_w, self.five_min_h, self.scene(), self.db)
                self.scene().addItem(self.new_block)
            elif event.button() == Qt.MouseButton.RightButton:
                self.drop_new_block()
        if event.button() == Qt.MouseButton.LeftButton and self.mode!='move':
            item = self.itemAt(event.pos())
            if isinstance(item, (LessonBlock, QGraphicsTextItem)):
                item.bring_back()
                item.setSelected(False)
            item = self.itemAt(event.pos())
            if isinstance(item, (LessonBlock, QGraphicsTextItem)):
                item.bring_forward()

        # if event.button() == Qt.MouseButton.RightButton:
        #     item = self.itemAt(event.pos())
        #     if isinstance(item, LessonBlock):
        #         item.contextMenuEvent(event)
    
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, (QGraphicsTextItem, LessonBlock)):
            item.contextMenuEvent(event)
        # return super().contextMenuEvent(event)


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.new_block:
            # add new block to db
            # find (sub)class
            x = self.new_block.boundingRect().x() - self.left_bar_w + 1
            i = x // self.block_w
            i = int(i%len(self.classes))
            my_class = self.classes[i]
            # print(i, my_class.full_name())
            # find if block spans entire class
            # either is wide
            if self.new_block.boundingRect().width() -1 > self.block_w:
                my_class = my_class.get_class()
            # ... or is the only subclass
            if len(my_class.get_class().subclasses)==1:
                my_class = my_class.get_class()
            # print(my_class.full_name())
            # find day
            day = int(x // self.day_w)
            y = self.new_block.boundingRect().y() - self.top_bar_h + 1
            start = int(y // self.five_min_h)
            length = int(self.new_block.boundingRect().height() // self.five_min_h)
            # print(f'start: {start}, length {length}')
            block = self.db.create_block(day, start, length, my_class)
            self.new_block.block = block
            self.new_block.set_selectable(True)
            self.blocks.append(self.new_block)
            pass
        self.block_start = -1
        self.new_block = False
        # self.draw_frame()


    
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

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.mode == 'new':
            # stop if moved out of bounds:
            if (event.y() < self.top_bar_h or event.x() < self.left_bar_w):
                self.drop_new_block()
                return
            
            # show tooltip
            now = self.how_many_5_min_blocks(event)
            times = [now, self.block_start] if self.block_start >=0 else [now]
            times.sort()
            msg = '-'.join([display_hour(t) for t in times])
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
        x1 = (self.new_block_left - self.left_bar_w)%self.day_w + 2
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
            class_names = [c.full_name() for c in self.classes]
            # print(ids)
            for z, block in enumerate(self.db.all_blocks()):
                # class not represented
                full_name = block.parent().full_name()
                if full_name not in class_names:
                    # either is a subclass
                    if isinstance(block.parent(), Subclass):
                        continue
                    
                    # find first subclass that is shown
                    n = -1
                    for subclass in block.parent().subclasses:
                        if subclass.full_name() in class_names:
                            n = class_names.index(subclass.full_name())
                            break
                    # if none are found don't draw the block
                    if n < 0:
                        continue
                else:
                    n = class_names.index(full_name)
                    
                
                x = self.left_bar_w + self.day_w*block.day + n*self.block_w

                y = self.five_min_h*block.start+ self.top_bar_h

                # stretch the width if needed
                if isinstance(block.parent(), Class):
                    mask = [1 if cl.get_class().id == block.parent().id else 0 for cl in self.classes]
                    witdth_multiplier = sum(mask)
                else:
                    witdth_multiplier = 1
                width = self.block_w*witdth_multiplier
                
                height = self.five_min_h* block.length


                new_block = LessonBlock(x, y, width, height, self.scene(), self.db)
                new_block.setZValue(z+10000)
                new_block.block = block
                new_block.start = block.start
                new_block.draw_lessons(self.classes)

                new_block.set_movable(self.mode=='move', self.five_min_h, self.top_bar_h)
                self.blocks.append(new_block)
                new_block.set_selectable(True)
                self.scene().addItem(new_block)
                # rect.setPen(wide_pen)
                # rect.setZValue(200)
                # print(rect)


        

