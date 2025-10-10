import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
from PyQt6.QtCore import QSize, QCoreApplication

from PyQt6.QtSql import QSqlDatabase
from sqlalchemy.orm import Session
from db import engine


from widgets.subjects import SubjectsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monte Planer")
        self.setMinimumSize(QSize(400, 300))

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)

        tabs.addTab(QWidget(), "Plan")
        tabs.addTab(SubjectsWidget(), "Przedmioty")
        tabs.addTab(QWidget(), "Klasy")
        tabs.addTab(QWidget(), "Nauczyciele")

        self.setCentralWidget(tabs)

app = QApplication(sys.argv)
# print(open_connection())
window = MainWindow()
window.show()
app.exec()