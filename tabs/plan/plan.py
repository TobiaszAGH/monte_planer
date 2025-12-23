from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt
from data import Data
from .mode_btn import ModeBtn
from .plan_view import MyView

        

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
        tool_add_block = ModeBtn("Nowy blok zajęciowy", self.set_mode_new, toolbar)
        toolbar.layout().addWidget(tool_add_block)
        tool_move_block = ModeBtn("Przesuwanie", self.set_mode_move ,toolbar)
        toolbar.layout().addWidget(tool_move_block)
        self.tool_add_custom = ModeBtn("Nowy blok", self.set_mode_new_custom ,toolbar)
        toolbar.layout().addWidget(self.tool_add_custom)
        self.scale_slider = QSlider(Qt.Horizontal, self)
        self.scale_slider.setMaximumWidth(150)
        self.scale_slider.setMinimum(100)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setSingleStep(10)
        self.scale_slider.setPageStep(50)
        self.scale_slider.setTickPosition(QSlider.TicksAbove | QSlider.TicksBelow)
        self.scale_slider.setTickInterval(50)
        self.scale_slider.valueChanged.connect(self.update_scale)
        toolbar.layout().addWidget(self.scale_slider)
        self.scale_label = QLabel('100%', self.scale_slider)
        toolbar.layout().addWidget(self.scale_label)
        toolbar.layout().addStretch()
        

        self.view = MyView(self)
        layout.addWidget(self.view)
        self.load_data()

    def update_scale(self, value):
        self.scale_label.setText(f'{value}%')
        self.view.resetTransform()
        self.view.scale(value/100, value/100)
        
    def set_mode_new(self, checked):
        if checked:
            self.view.set_mode('new')
        else:
            self.view.set_mode('normal')

    def set_mode_new_custom(self, checked):
        if checked:
            self.view.set_mode('new_custom')
            for button in self.class_filter.findChildren(QPushButton):
                button.setChecked(True)
            self.update_filter() 
        else:
            self.view.set_mode('normal')
    
    def set_mode_move(self, checked):
        if checked:
            self.view.set_mode('move')
        else:
            self.view.set_mode('normal')
    

    def load_classes(self):
        self.classes = []
        for my_class in self.db.all_classes():
            l = len(my_class.subclasses)
            if l == 1:
                self.classes.append(my_class)
            else:
                for subclass in my_class.subclasses:
                    self.classes.append(subclass)

        for widget in self.class_filter.findChildren(QPushButton):
            widget.deleteLater()

        for my_class in self.classes[::-1]:
            button = QPushButton(my_class.full_name())
            button.setCheckable(True)
            button.setChecked(True)
            button.my_class = my_class
            button.clicked.connect(self.filter_btn_clicked)
            self.class_filter.layout().insertWidget(0, button)

    def filter_btn_clicked(self):
        self.tool_add_custom.uncheck()
        self.view.set_mode('normal')
        self.update_filter()

    def update_filter(self):
        display_names = []
        for button in self.class_filter.findChildren(QPushButton):
            if button.isChecked():
                display_names.append(button.my_class)
        self.view.set_classes(display_names[::-1])
        self.view.draw()

    def load_data(self):
        self.load_classes()
        if self.classes:
            self.view.set_classes(self.classes)
            self.view.draw()
