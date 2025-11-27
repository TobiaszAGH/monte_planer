from PyQt5.QtWidgets import QTabWidget, QWidget
from widgets.classes import ClassesWidget
from widgets.subjects import SubjectsWidget
from widgets.teachers import TeachersWidget

class Tabs(QTabWidget):
    def __init__(self, data):
        super().__init__()
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setMovable(True)


        self.data = data
        self.subjects = SubjectsWidget(self, self.data)
        self.classes = ClassesWidget(self, self.data)
        self.teachers = TeachersWidget(self, self.data)


        self.addTab(QWidget(), "Plan")
        self.addTab(self.subjects, 'Przedmioty')
        self.addTab(self.classes, 'Klasy')
        self.addTab(self.teachers, "Nauczyciele")
        self.currentChanged.connect(self.refresh)

    def refresh(self):
        try:
            self.currentWidget().load_data(self.data)
        except:
            pass

    def load_data(self, data):
        self.data = data
        self.classes.load_data(self.data)
        self.teachers.load_data(self.data)
        self.subjects.load_data(self.data)