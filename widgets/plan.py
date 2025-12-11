
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
        self.classes = self.db.all_classes()
        display_names = []
        widths = []
        for my_class in self.classes:
            l = len(my_class.subclasses)
            widths.append(l)
            if l == 1:
                display_names.append(my_class)
            else:
                for subclass in my_class.subclasses:
                    display_names.append(subclass)

        if not display_names:
            return []
        
        for widget in self.class_filter.findChildren(QCheckBox):
            widget.deleteLater()

        for my_class in display_names[::-1]:
            checkbox = QCheckBox()
            checkbox.setText(my_class.name)
            checkbox.setChecked(True)
            checkbox.clicked.connect(self.update_filter)
            self.class_filter.layout().insertWidget(0, checkbox)
        return display_names, widths

    def update_filter(self):
        display_names = []
        for checkbox in self.class_filter.findChildren(QCheckBox):
            if checkbox.isChecked():
                display_names.append(checkbox.text())
        self.view.set_class_names(display_names[::-1])
        self.view.draw_frame()

    def load_data(self):
        display_names, widths = self.load_classes()
        self.view.set_class_names(display_names, widths)
        self.view.draw_frame()
