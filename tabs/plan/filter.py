from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QPushButton
from .mode_btn import ModeBtn
from data import Class

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
        def filter(l):
            return isinstance(l.subject.parent(), Class) \
                or l.subject.parent() in display_names \
                or len(l.subject.parent().get_class().subclasses) == 1
        self.view.set_classes(display_names)
        self.view.filter_func = filter
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

        for my_class in self.classes:
            button = QPushButton(my_class.full_name())
            button.setCheckable(True)
            button.setChecked(True)
            button.my_class = my_class
            button.clicked.connect(self.filter_btn_clicked)
            index = self.layout().count()-1
            self.layout().insertWidget(index, button)



