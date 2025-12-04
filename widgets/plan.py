
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QDialog, QDialogButtonBox, \
      QPushButton, QLabel, QDialogButtonBox, QMessageBox, QInputDialog, QGridLayout, QCheckBox, QSizePolicy, \
      QGraphicsScene, QGraphicsView, QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen


class MyView(QGraphicsView):

    def __init__(self,parent, data):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.data = data
        self.class_names = []

    def set_class_names(self, class_names):
        self.class_names = class_names

    def resizeEvent(self, event):
        QGraphicsView.resizeEvent(self, event)
        self.draw_frame()

    def draw_frame(self):
        scene = self.scene()
        scene.clear()
        width = self.geometry().width()-10
        height = self.geometry().height()-10
        top_bar_h = 75
        left_bar_w = 50


        scene.setSceneRect(0,0, width, height)

        wide_pen = QPen()
        wide_pen.setWidth(2)
        line = scene.addLine(0, top_bar_h, width, top_bar_h)
        line.setPen(wide_pen)
        line = scene.addLine(0, 0, width, 0)
        line.setPen(wide_pen)
        line = scene.addLine(0, 0, 0, height)
        line.setPen(wide_pen)
        line = scene.addLine(0, height, width, height)
        line.setPen(wide_pen)
        line = scene.addLine(left_bar_w, 0, left_bar_w, height)
        line.setPen(wide_pen)

        hour_h = (height-top_bar_h)/8
        five_min_h = hour_h*12
        for hour in range(8,16):
            pos = top_bar_h+(hour - 7)*hour_h
            text = scene.addSimpleText(f'{hour}-{hour+1}')

            # center text
            text_x = (left_bar_w-text.boundingRect().width())/2
            text_y = pos-(hour_h+text.boundingRect().height())/2
            text.setPos(text_x, text_y)

            scene.addLine(0, pos, left_bar_w, pos)

        l = len(self.class_names)
        day_w = (width-left_bar_w)/5
        days = 'Poniedziałek Wtorek Środa Czwartek Piątek'.split()
        for day in range(5):
            pos = day_w*(day+1)+left_bar_w
            line = scene.addLine(pos, 0, pos, height)
            line.setPen(wide_pen)
            
            text = scene.addSimpleText(days[day])
            text_x = pos - (day_w + text.boundingRect().width())/2
            text_y = (top_bar_h/2 - text.boundingRect().height())/2
            text.setPos(text_x, text_y)
        if l>0:
            scene.addLine(left_bar_w, top_bar_h/2, width, top_bar_h/2)
            block_w = day_w/l
            for i in range(5):
                for n, class_name in enumerate(self.class_names):
                    pos = block_w*(n+i*l+1)+left_bar_w
                    text = scene.addSimpleText(class_name)
                    text_x = pos - (text.boundingRect().width()+block_w)/2
                    text_y = top_bar_h/2 + (top_bar_h/2 - text.boundingRect().height())/2
                    text.setPos(text_x, text_y)
                    scene.addLine(pos, top_bar_h/2, pos, height)


        

        

class PlanWidget(QWidget):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        layout = QVBoxLayout(self)
        self.setLayout(layout)


        self.class_filter = QWidget()
        self.class_filter.setLayout(QHBoxLayout())
        self.class_filter.layout().addStretch()
        self.load_classes()
        layout.addWidget(self.class_filter)
        self.view = MyView(self, self.data)
        layout.addWidget(self.view)
        self.load_data(data)

    

    def load_classes(self):
        class_names = self.data['classes'].keys()
        display_names = []
        for class_name in class_names:
            subclasses = self.data['classes'][class_name]['students'].keys()
            if len(subclasses) == 1:
                display_names.append(class_name)
            else:
                full_subclass_names = [f'{class_name}{s}' for s in subclasses]
                display_names.extend(full_subclass_names)

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

    def load_data(self, data):
        self.data = data
        display_names = self.load_classes()
        self.view.set_class_names(display_names)
        self.view.draw_frame()
