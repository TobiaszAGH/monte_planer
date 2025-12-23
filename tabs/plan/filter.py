from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QPushButton, QGridLayout, QStackedLayout, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt
from .mode_btn import ModeBtn
from data import Class

class FilterWidget(QWidget):
    def __init__(self, parent, view, tool_add_custom):
        super().__init__(parent)
        self.view = view
        self.db = parent.db
        self.tool_add_custom = tool_add_custom

        main_layout = QGridLayout()
        self.setLayout(main_layout)
        main_layout.setColumnStretch(0,1)
        main_layout.setColumnStretch(1,2)

        filter_selection = QComboBox()
        items = 'Klasy Uczniowie Nauczyciele Sale'.split()
        filter_selection.addItems(items)
        main_layout.addWidget(filter_selection, 0, 0)

        self.stacked = QStackedWidget()
        self.stacked.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        main_layout.addWidget(self.stacked, 0, 1)

        # classes
        self.class_filter = QWidget()
        self.class_filter.setLayout(QHBoxLayout())
        self.stacked.layout().addWidget(self.class_filter)

        # students
        self.student_filter = QWidget()
        self.student_filter.setLayout(QHBoxLayout())
        self.student_class_selection = QComboBox()



    
    def filter_btn_clicked(self):
        self.tool_add_custom.uncheck()
        self.view.set_mode('normal')
        self.update_class_filter()

    def update_class_filter(self):
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

        for index, my_class in enumerate(self.classes):
            self.student_class_selection.addItem(my_class.full_name(), my_class)
            button = QPushButton(my_class.full_name())
            button.setCheckable(True)
            button.setChecked(True)
            button.my_class = my_class
            button.clicked.connect(self.filter_btn_clicked)
            self.class_filter.layout().insertWidget(index, button)



