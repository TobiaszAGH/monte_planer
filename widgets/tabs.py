from PyQt5.QtWidgets import QTabWidget, QWidget
from widgets.classes import ClassesWidget
from widgets.subjects import SubjectsWidget

class Tabs(QTabWidget):
    def __init__(self, data):
        super().__init__()
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setMovable(True)


        self.data = data
        self.subjects = SubjectsWidget(self, self.data)
        self.classes = ClassesWidget(self, self.data)


        self.addTab(QWidget(), "Plan")
        self.addTab(self.subjects, 'Przedmioty')
        self.addTab(self.classes, 'Klasy')
        self.addTab(QWidget(), "Nauczyciele")

    def load_data(self, data):
        self.data = data
        self.classes.load_data(self.data)