from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QPushButton
from .mode_btn import ModeBtn

class FilterWidget(QWidget):
    def __init__(self, parent, view, tool_add_custom):
        super().__init__(parent)
        self.view = view
        self.db = parent.db
        self.setLayout(QHBoxLayout())
        self.layout().addStretch()
        self.tool_add_custom = tool_add_custom
        # self.load_classes()

    
    def filter_btn_clicked(self):
        self.tool_add_custom.uncheck()
        self.view.set_mode('normal')
        self.update_filter()

    def update_filter(self):
        display_names = []
        for button in self.findChildren(QPushButton):
            if button.isChecked():
                display_names.append(button.my_class)
        self.view.set_classes(display_names[::-1])
        self.view.draw()

    def load_classes(self):
        self.classes = []
        for my_class in self.db.all_classes():
            l = len(my_class.subclasses)
            if l == 1:
                self.classes.append(my_class)
            else:
                for subclass in my_class.subclasses:
                    self.classes.append(subclass)

        for widget in self.findChildren(QPushButton):
            widget.deleteLater()

        for my_class in self.classes[::-1]:
            button = QPushButton(my_class.full_name())
            button.setCheckable(True)
            button.setChecked(True)
            button.my_class = my_class
            button.clicked.connect(self.filter_btn_clicked)
            self.layout().insertWidget(0, button)



