from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt
from data import Data
from .mode_btn import ModeBtn
from .plan_view import MyView
from.filter import FilterWidget

        

class PlanWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.db: Data = parent.db
        layout = QVBoxLayout(self)
        self.setLayout(layout)




        toolbar = QWidget()
        toolbar.setLayout(QHBoxLayout())
        tool_add_block = ModeBtn("Nowy blok zajęciowy", self.set_mode_new, toolbar)
        toolbar.layout().addWidget(tool_add_block)
        tool_move_block = ModeBtn("Przesuwanie", self.set_mode_move ,toolbar)
        toolbar.layout().addWidget(tool_move_block)
        tool_add_custom = ModeBtn("Nowy blok", self.set_mode_new_custom ,toolbar)
        toolbar.layout().addWidget(tool_add_custom)
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
        self.class_filter = FilterWidget(self, self.view, tool_add_custom)
        

        layout.addWidget(self.class_filter)
        layout.addWidget(toolbar)
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
            self.class_filter.update_filter() 
        else:
            self.view.set_mode('normal')
    
    def set_mode_move(self, checked):
        if checked:
            self.view.set_mode('move')
        else:
            self.view.set_mode('normal')
    
    def load_data(self):
        self.class_filter.load_classes()
        if self.class_filter.classes:
            self.view.set_classes(self.class_filter.classes)
            self.view.draw()
