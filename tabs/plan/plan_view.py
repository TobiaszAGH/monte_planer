from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QToolTip, QGraphicsTextItem, QGraphicsRectItem
from PyQt5.QtGui import QPen, QColor, QBrush, QTransform
from PyQt5.QtCore import QPoint, Qt, QRectF
from networkx import Graph
import gcol
from .lesson_block import LessonBlock
from .custom_block import CustomBlock
from .block import BasicBlock
from functions import snap_position, display_hour, contrast_ratio
from data import Data, Class, Subclass, LessonBlockDB
from db_config import settings


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
        def filter(l):
            return True
        self.filter_func = filter

    def uncheck_all_modes(self):
        self.parent().uncheck_all_modes()
        self.set_mode('normal')
    

    def set_classes(self, classes):
        self.widths = [0]
        self.classes = classes
        if not len(classes):
            self.class_names = []
            self.update_column_sizes()
            return
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
        self.draw()

    def set_mode(self, mode):
        self.mode = mode
        for block in self.scene().items():
            if isinstance(block, BasicBlock):
                block.set_movable(mode=='move', self.five_min_h, self.top_bar_h)
                block.set_selectable(mode not in ('new', 'new_custom'))
                
    
    def mousePressEvent(self, event):
        if self.mode in ('new', 'new_custom'):
            if event.button() == Qt.MouseButton.LeftButton:
                l = len(self.class_names)
                if l == 0:
                    return 
                self.block_start = self.how_many_5_min_blocks(event)
                self.new_block_top = snap_position(self.mapToScene(event.pos()).y(), self.five_min_h, self.top_bar_h)
                self.new_block_left = snap_position(self.mapToScene(event.pos()).x(), self.block_w, self.left_bar_w)
                if self.mode == 'new':
                    self.new_block = LessonBlock(self.new_block_left, self.new_block_top, self.block_w, self.five_min_h, self.scene(), self.db, self.classes)
                elif self.mode == 'new_custom':
                    self.new_block = CustomBlock(self.new_block_left, self.new_block_top, self.block_w, self.five_min_h, self.scene(), self.db, self.classes)
                self.new_block.bring_forward()
                self.new_block.setBrush(QBrush(QColor('#c0c0c0')))
                
                self.scene().addItem(self.new_block)
            elif event.button() == Qt.MouseButton.RightButton:
                self.drop_new_block()
        if event.button() == Qt.MouseButton.LeftButton and self.mode!='move':
            item = self.itemAt(event.pos())
            if isinstance(item, (BasicBlock, QGraphicsTextItem)):
                item.bring_back()
                item.setSelected(False)
            item = self.itemAt(event.pos())
            if isinstance(item, (BasicBlock, QGraphicsTextItem)):
                item.bring_forward()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, (QGraphicsTextItem, LessonBlock, CustomBlock)):
            item.contextMenuEvent(event)


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.new_block:
            self.new_block.setBrush(QColor(0,0,0,0))
            # drop block if it has no length:
            if self.new_block.boundingRect().height() < self.five_min_h:
                self.new_block.delete()
                self.new_block = ''
                return
            # add new block to db
            # find day
            x = self.new_block.boundingRect().x() - self.left_bar_w + 1
            day = int(x // self.day_w)
            y = self.new_block.boundingRect().y() - self.top_bar_h + 1
            start = int(y // self.five_min_h)
            length = int(self.new_block.boundingRect().height() // self.five_min_h)
            # find (sub)class
            i = x // self.block_w
            i = int(i%len(self.classes))
            if self.mode == 'new':
                my_class = self.classes[i]
                # find if block spans entire class
                # either is wide
                if self.new_block.boundingRect().width() -1 > self.block_w:
                    my_class = my_class.get_class()
                # ... or is the only subclass
                if len(my_class.get_class().subclasses)==1:
                    my_class = my_class.get_class()
            
                block = self.db.create_block(day, start, length, my_class)

            elif self.mode =='new_custom':
                n_of_classes = int(self.new_block.boundingRect().width()//self.block_w)
                classes = self.classes[i:i+n_of_classes]
                subclasses = [s.subclasses[0] if isinstance(s, Class) else s for s in classes]
                block: CustomBlock = self.db.create_custom_block(day, start, length, subclasses)
                self.new_block.block = block
                self.new_block.pick_color()
                self.new_block.set_text()

            # print(my_class.full_name())
            self.new_block.block = block
            self.new_block.set_selectable(True)
            self.new_block.draw_contents()
            self.blocks.append(self.new_block)
        self.block_start = -1
        self.new_block = False


    
    def how_many_5_min_blocks(self, event):
        y = self.mapToScene(event.pos()).y() - self.top_bar_h
        mins = y//self.five_min_h
        return mins

    def drop_new_block(self):
        if self.new_block:
            self.scene().removeItem(self.new_block)
        self.new_block = False
        self.block_start = -1
        QToolTip.showText(QPoint(), '')

    def mouseMoveEvent(self, event):
        # show tooltip
        item = self.itemAt(event.pos())
        if not item or self.new_block:
            now = self.how_many_5_min_blocks(event)
            times = [now, self.block_start] if self.block_start >=0 else [now]
            times.sort()
            msg = '-'.join([display_hour(t) for t in times])
            if self.block_start>=0:
                msg += f' ({int(abs(now-self.block_start)*5)})'
            QToolTip.showText(event.globalPos(), msg)
        else:
            QToolTip.showText(event.globalPos(), '')


        super().mouseMoveEvent(event)
        if self.mode in ('new', 'new_custom'):
            # stop if moved out of bounds:
            if (event.y() < self.top_bar_h or event.x() < self.left_bar_w):
                self.drop_new_block()
                return
            
                        # update block
            if self.new_block:
                self.new_block.bring_forward()
                cursor_x = snap_position(self.mapToScene(event.pos()).x(), self.block_w, self.left_bar_w)
                x, width = self.calculate_x_w(cursor_x)
                
                new_block_bottom = snap_position(self.mapToScene(event.pos()).y(), self.five_min_h, self.top_bar_h)
                height = abs(new_block_bottom - self.new_block_top)
                y = min(new_block_bottom, self.new_block_top)
                self.new_block.setRect(x, y, width, height)


    def calculate_x_w(self, cursor_x):
        # if in the same subclass block dont stretch
        if self.new_block_left==cursor_x:
            return self.new_block_left, self.block_w

        if self.mode == 'new':
            # get the bottom boundry
            x1 = (self.new_block_left - self.left_bar_w)%self.day_w + 2
            for boundry in self.boundries:
                if x1>=boundry:
                    bottom = boundry
            
            day_start = snap_position(self.new_block_left, self.day_w, self.left_bar_w)
            x = bottom+day_start
            top = self.boundries[self.boundries.index(bottom)+1]
            w = top-bottom

        elif self.mode == 'new_custom':
            left, right = sorted([self.new_block_left, cursor_x])
            day_start = snap_position(self.new_block_left, self.day_w, self.left_bar_w)
            day_end = day_start + self.day_w
            left = max(day_start, left)
            right = min(day_end, right+self.block_w) 
            x = left
            w = right - left
        return x,w

    def draw_frame(self):
        scene = self.scene()
        wide_pen = QPen()
        wide_pen.setWidth(3)
        line = scene.addLine(0, self.top_bar_h, self.scene_width, self.top_bar_h, wide_pen)
        line = scene.addLine(0, 0, self.scene_width, 0, wide_pen)
        line = scene.addLine(0, 0, 0, self.scene_height, wide_pen)
        line = scene.addLine(0, self.scene_height, self.scene_width, self.scene_height, wide_pen)
        line = scene.addLine(self.left_bar_w, 0, self.left_bar_w, self.scene_height, wide_pen)

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
            line.setZValue(10000)
            line.setPen(wide_pen)
            
            text = scene.addSimpleText(days[day])
            text_x = pos - (self.day_w + text.boundingRect().width())/2
            text_y = (self.top_bar_h/2 - text.boundingRect().height()/2)\
                /(2 if not settings.draw_blocks_full_width else 1)
            text.setPos(text_x, text_y)
        self.draw_headers = l>0 and not settings.draw_blocks_full_width
        if self.draw_headers:
            
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


    def place_block(self, block):
        # class_names = [c.full_name() for c in self.classes]
        if settings.draw_blocks_full_width:
            n = 0
            width_multiplier = len(self.classes)
        elif isinstance(block, LessonBlockDB):
            # find subclass
            if block.subclass in self.classes:
                n = self.classes.index(block.subclass)
            # find first subclass
            elif block.my_class:
                n = -1
                for subclass in block.my_class.subclasses:
                    if subclass in self.classes:
                        n = self.classes.index(subclass)
                        break
                # if none are found don't draw the block
                if n < 0:
                    return
            else:
                return

            # stretch the width if needed
            if block.my_class:
                mask = [1 if cl.get_class().id == block.class_id else 0 for cl in self.classes]
                width_multiplier = sum(mask)
            else:
                width_multiplier = 1
            

        else:
            ns = []
            width_multiplier = 0
            for subclass in block.subclasses:
                if subclass in self.classes:
                    ns.append(self.classes.index(subclass))
                    width_multiplier += 1
            if len(ns) == 0:
                return
            
            n = min(ns)

        x = self.left_bar_w + self.day_w*block.day + n*self.block_w
        y = self.five_min_h*block.start+ self.top_bar_h
        width = self.block_w*width_multiplier
        height = self.five_min_h * block.length

        if isinstance(block, LessonBlockDB):
            return LessonBlock(x, y, width, height, self.scene(), self.db, self.classes)
            
        else:
            if not settings.draw_custom_blocks:
                return
            return CustomBlock(x, y, width, height, self.scene(), self.db, self.classes)
                

    def draw_blocks(self, blocks):
        for z, block in enumerate(blocks):
            new_block = self.place_block(block)
            if not new_block:
                continue

            new_block.block = block
            if isinstance(new_block, LessonBlock): 
                new_block.setZValue(z+5000)
                # new_block.write(not self.draw_headers)
            else:
                new_block.setZValue(z+2000)
            new_block.start = block.start
            new_block.set_filter(self.filter_func)
            new_block.draw_contents()

            new_block.set_movable(self.mode=='move', self.five_min_h, self.top_bar_h)
            self.blocks.append(new_block)
            new_block.set_selectable(True)
            new_block.update()
            self.scene().addItem(new_block)

    def narrow_overlapping_blocks(self):
        # for each day
        for day in range(5):

            # get blocks in every day
            x = self.left_bar_w + self.day_w*day + 10
            y = self.top_bar_h
            width = self.day_w -30
            height = self.scene_height - self.top_bar_h
            day_rect = QRectF(x, y, width, height)
            blocks = [bl for bl in self.scene().items(day_rect) if isinstance(bl, LessonBlock)]
            if not len(blocks):
                continue


            # generate graph
            graph = Graph()
            for block in blocks:
                graph.add_node(block.block.id)
            for block in blocks:
                for col_block in block.overlapping_lesson_blocks():
                    if graph.has_edge(block.block.id, col_block.block.id):
                        continue
                    graph.add_edge(block.block.id, col_block.block.id)

            # graph.

            
            # color graph
            colored = gcol.node_coloring(graph)
            num_of_colors = max(list(colored.values()))+1

            for block in blocks:
                if not len(block.overlapping_lesson_blocks()):
                    continue
                color = colored[block.block.id]
                
                dx = (color+day)*self.day_w+self.left_bar_w
                transform = QTransform()
                transform.scale(1/num_of_colors, 1)
                transform.translate(dx, 0)
                block.setTransform(transform, combine=True)
                block.write()



         

    def draw(self):
        scene = self.scene()
        scene.clear()
        scene.setSceneRect(0,0, self.scene_width, self.scene_height)

        self.draw_frame()

        if len(self.classes):
            self.draw_blocks(self.db.all_blocks())

            # self.draw_blocks(self.db.all_lesson_blocks())
            # self.draw_blocks(self.db.all_custom_blocks())

    def load_data(self, db):
        self.db = db

