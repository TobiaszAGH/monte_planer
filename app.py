import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
from PyQt5.QtCore import QSize


from data import blank_data
from widgets.subjects import SubjectsWidget
from widgets.classes import ClassesWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = blank_data()

        self.setWindowTitle("Monte Planer")
        self.setMinimumSize(QSize(400, 300))

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)

        tabs.addTab(QWidget(), "Plan")
        tabs.addTab(SubjectsWidget(self, self.data), "Przedmioty")
        tabs.addTab(ClassesWidget(self, self.data), "Klasy")
        tabs.addTab(QWidget(), "Nauczyciele")

        self.setCentralWidget(tabs)

app = QApplication(sys.argv)
# print(open_connection())
window = MainWindow()
window.show()
app.exec()