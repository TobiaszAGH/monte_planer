
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QDialog, QDialogButtonBox, \
      QPushButton, QLabel, QDialogButtonBox, QMessageBox, QInputDialog, QGridLayout, QCheckBox, QSizePolicy, \
      QGraphicsScene, QGraphicsView, QSpacerItem, QToolBar, QToolTip, QGraphicsItem, QGraphicsRectItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush

from data import Data, Class


class MyView(QGraphicsView):

    def __init__(self,parent):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.db = parent.db
        self.class_names = []
        self.mode = ''
        self.block_start = 0
        self.new_block = False
        self.setMouseTracking(True)
        self.top_bar_h = 75
        self.left_bar_w = 50
        self.update_size_params()

    def set_class_names(self, class_names):
        self.class_names = class_names

    def update_size_params(self):
        self.scene_width = self.geometry().width()-10
        self.scene_height = self.geometry().height()-10
        self.hour_h = (self.scene_height-self.top_bar_h)/8
        self.five_min_h = self.hour_h/12
        self.day_w = (self.scene_width-self.left_bar_w)/5
        l = len(self.class_names)
        if l>0:
            self.block_w = self.day_w/l

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)

        self.update_size_params()
        self.draw_frame()

    def set_mode_new(self):
        self.mode = 'new'
    
    def mousePressEvent(self, event):
        if self.mode == 'new':
            l = len(self.class_names)
            if l == 0:
                return False
            self.block_start = self.how_many_5_min_blocks(event)
            self.new_block_top = (event.y() - self.top_bar_h) // self.five_min_h * self.five_min_h + self.top_bar_h
            self.new_block_left = (event.x() - self.left_bar_w) // self.block_w * self.block_w + self.left_bar_w
            self.new_block = self.scene().addRect(self.new_block_left, self.new_block_top, self.block_w, self.five_min_h)


    def mouseReleaseEvent(self, event):
        self.block_start = 0
        self.new_block = False
        # if self.mode == 'new':

    def display_hour(self, mins):
        hs = int(mins//12+8)
        mins = int(mins%12)*5
        return f'{hs}:{mins:02d}' 
    
    def how_many_5_min_blocks(self, event):
        y = event.y() - self.top_bar_h
        mins = y//self.five_min_h
        return mins
        

    def mouseMoveEvent(self, event=0):
        if self.mode == 'new':
            now = self.how_many_5_min_blocks(event)
            times = [now, self.block_start] if self.block_start else [now]
            times.sort()
            msg = '-'.join([self.display_hour(t) for t in times])
            if self.block_start:
                msg += f' ({int(abs(now-self.block_start)*5)})'

            QToolTip.showText(event.globalPos(), msg)
            if self.new_block:
                new_block_bottom = (event.y() - self.top_bar_h) // self.five_min_h * self.five_min_h + self.top_bar_h
                height = abs(new_block_bottom - self.new_block_top)
                y = min(new_block_bottom, self.new_block_top)
                self.new_block: QGraphicsRectItem
                
                self.new_block.setRect(self.new_block_left, y, self.block_w, height)
                # print(self.new_block)
        pass

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

        l = len(self.class_names)
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


        

        

class PlanWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.db: Data = parent.db
        layout = QVBoxLayout(self)
        self.setLayout(layout)


        self.class_filter = QWidget()
        self.class_filter.setLayout(QHBoxLayout())
        self.class_filter.layout().addStretch()
        self.load_classes()
        layout.addWidget(self.class_filter)


        toolbar = QWidget()
        layout.addWidget(toolbar)
        toolbar.setLayout(QHBoxLayout())
        tool_add_block = QPushButton("N", toolbar)
        toolbar.layout().addWidget(tool_add_block)
        tool_add_block.setAutoExclusive(True)
        tool_add_block.setCheckable(True)
        tool_add_block.clicked.connect(self.set_mode_new)
        tool_move_block = QPushButton("M", toolbar)
        toolbar.layout().addWidget(tool_move_block)
        tool_move_block.setAutoExclusive(True)
        tool_move_block.setCheckable(True)
        

        self.view = MyView(self)
        layout.addWidget(self.view)
        self.load_data()

        
        
    def set_mode_new(self):
        self.view.set_mode_new()

    

    def load_classes(self):
        classes = self.db.all_classes()
        display_names = []
        for my_class in classes:
            if len(my_class.subclasses) == 1:
                display_names.append(my_class.name)
            else:
                for subclass in my_class.subclasses:
                    display_names.append(subclass.full_name())

        if not display_names:
            return []
        
        for widget in self.class_filter.findChildren(QCheckBox):
            widget.deleteLater()

        for class_name in display_names[::-1]:
            checkbox = QCheckBox()
            checkbox.setText(class_name)
            checkbox.setChecked(True)
            checkbox.clicked.connect(self.update_filter)
            self.class_filter.layout().insertWidget(0, checkbox)
        return display_names

    def update_filter(self):
        display_names = []
        for checkbox in self.class_filter.findChildren(QCheckBox):
            if checkbox.isChecked():
                display_names.append(checkbox.text())
        self.view.set_class_names(display_names[::-1])
        self.view.draw_frame()

    def load_data(self):
        display_names = self.load_classes()
        # self.view.data = data
        self.view.set_class_names(display_names)
        self.view.draw_frame()
