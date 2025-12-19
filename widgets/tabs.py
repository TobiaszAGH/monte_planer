from PyQt5.QtWidgets import QTabWidget
from widgets.classes import ClassesWidget
from widgets.subjects import SubjectsWidget
from widgets.teachers import TeachersWidget
from widgets.plan import PlanWidget
from widgets.classrooms import ClassroomsWidget

class Tabs(QTabWidget):
    def __init__(self, parent, data):
        super().__init__()
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setMovable(True)

        self.db = parent.db
        self.subjects = SubjectsWidget(self)
        self.classes = ClassesWidget(self)
        self.teachers = TeachersWidget(self)
        self.plan = PlanWidget(self)
        self.classrooms = ClassroomsWidget(self)


        self.addTab(self.plan, "Plan")
        self.addTab(self.subjects, 'Przedmioty')
        self.addTab(self.classes, 'Klasy')
        self.addTab(self.teachers, "Nauczyciele")
        self.addTab(self.classrooms, 'Pomieszczenia')
        self.currentChanged.connect(self.refresh)

    def refresh(self):
        try:
            self.currentWidget().load_data()
        except:
            pass

    def load_data(self):
        self.refresh()