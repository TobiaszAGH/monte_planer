import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction
from PyQt5.QtCore import QSize

import json
import os

from data import Data
from tabs import Tabs

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if not os.path.isfile('db_name'):
            with open('db_name', 'x') as f:
                pass
        
        with open('db_name', 'r+') as f:
            db_name = f.read().strip()
            if not db_name:
                db_name = 'planer.mtp'
            f.write(db_name)

        self.db = Data(db_name)



        self.setWindowTitle("Monte Planer")
        self.setMinimumSize(QSize(800, 800))
        self.tabs = Tabs(self)

        load_action = QAction('Wczytaj', self)
        load_action.triggered.connect(self.load_data)

        menu = self.menuBar()
        file_menu = menu.addMenu('&Plik')
        file_menu.addActions([
            load_action,
        ])


        self.setCentralWidget(self.tabs)


    def load_data(self):
        open_path, _ = QFileDialog.getOpenFileName(self, 'Wczytaj dane', '', '*.mtp', '*.mtp')
        if not open_path:
            return
        self.db = Data(open_path)
        self.tabs.load_data(self.db)
        with open('db_name', mode='w') as f:
            f.write(open_path)
        return True

app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
app.exec()