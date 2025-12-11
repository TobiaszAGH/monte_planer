
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox

from data import Data, Class
from widgets.plan_view import MyView

        

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
        self.classes = []
        for my_class in self.db.all_classes():
            l = len(my_class.subclasses)
            if l == 1:
                self.classes.append(my_class)
            else:
                for subclass in my_class.subclasses:
                    self.classes.append(subclass)

        for widget in self.class_filter.findChildren(QCheckBox):
            widget.deleteLater()

        for my_class in self.classes[::-1]:
            checkbox = QCheckBox()
            checkbox.setText(my_class.full_name())
            checkbox.setChecked(True)
            checkbox.my_class = my_class
            checkbox.clicked.connect(self.update_filter)
            self.class_filter.layout().insertWidget(0, checkbox)

    def update_filter(self):
        display_names = []
        for checkbox in self.class_filter.findChildren(QCheckBox):
            if checkbox.isChecked():
                display_names.append(checkbox.my_class)
        self.view.set_classes(display_names[::-1])
        self.view.draw_frame()

    def load_data(self):
        self.load_classes()
        if self.classes:
            self.view.set_classes(self.classes)
            self.view.draw_frame()
