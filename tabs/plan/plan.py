from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog,\
      QGraphicsTextItem, QStyleOptionGraphicsItem, QStackedWidget
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPainter, QTransform, QPixmap
from PyQt5.QtCore import Qt
from data import Data
from .mode_btn import ModeBtn
from .plan_view import MyView
from.filter import FilterWidget
from time import sleep
        

class PlanWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.db: Data = parent.db
        layout = QVBoxLayout(self)
        self.setLayout(layout)




        toolbar = QWidget()
        toolbar.setLayout(QHBoxLayout())
        self.tool_add_block = ModeBtn("Nowy blok zajęciowy", self.set_mode_new, toolbar)
        toolbar.layout().addWidget(self.tool_add_block)
        self.tool_move_block = ModeBtn("Przesuwanie", self.set_mode_move ,toolbar)
        toolbar.layout().addWidget(self.tool_move_block)
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

        export_btn = QPushButton('Eksportuj')
        toolbar.layout().addWidget(export_btn)
        export_btn.clicked.connect(self.render_scene_to_pixmap)
        # resize_btn = QPushButton('Resize')
        # toolbar.layout().addWidget(resize_btn)
        # resize_btn.clicked.connect(self.resize_view)

        self.view = MyView(self)
        self.hidden_view = MyView(self)
        self.class_filter = FilterWidget(self, self.view, self.tool_add_custom)
        
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_DontShowOnScreen, True)
        conlayout = QVBoxLayout(self.container)
        conlayout.addWidget(self.hidden_view)

        self.container.show()
        self.hidden_view.resize(2970, 2100)
        self.container.hide()

        layout.addWidget(self.class_filter)
        layout.addWidget(toolbar)
        # layout.addWidget(self.hidden_view)
        # self.hidden_view.show()
        # self.hidden_view.hide()
        layout.addWidget(self.view)
        self.load_data()

    def render_scene_to_pixmap(self):
        self.container.show()
        scene = self.hidden_view.scene()
        for text in [i for i in scene.items() if isinstance(i, QGraphicsTextItem)]:
            text.ensureVisible()
        rect = scene.sceneRect()

        pix = QPixmap(rect.size().toSize())
        pix.fill(Qt.white)

        painter = QPainter(pix)
        scene.render(painter)
        painter.end()
        filename, _ = QFileDialog.getSaveFileName(self, 'Eksportuj', 'plan.png')
        pix.save(filename, 'PNG', 100)
        self.container.hide()
 


    def update_scale(self, value):
        self.scale_label.setText(f'{value}%')
        self.view.resetTransform()
        self.view.scale(value/100, value/100)
        
    def set_mode_new(self, checked):
        if checked:
            self.class_filter.go_to_class_filter()
            self.view.set_mode('new')
        else:
            self.view.set_mode('normal')

    def set_mode_new_custom(self, checked):
        if checked:
            self.class_filter.go_to_class_filter()
            self.view.set_mode('new_custom')
            for button in self.class_filter.findChildren(QPushButton):
                button.setChecked(True)
            self.class_filter.update_class_filter() 
        else:
            self.view.set_mode('normal')
    
    def set_mode_move(self, checked):
        if checked:
            self.class_filter.go_to_class_filter()
            self.view.set_mode('move')
        else:
            self.view.set_mode('normal')

    def uncheck_all_modes(self):
        self.tool_add_block.uncheck()
        self.tool_add_custom.uncheck()
        self.tool_move_block.uncheck()
    
    def load_data(self):
        self.class_filter.load_data()
        if self.class_filter.classes:
            self.view.set_classes(self.class_filter.classes)
            self.view.draw()
            self.hidden_view.set_classes(self.class_filter.classes)
            self.hidden_view.draw()
