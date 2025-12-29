import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction
from PyQt5.QtCore import QSize

import shutil
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
            self.db_name = f.read().strip()
            if not self.db_name:
                self.db_name = 'planer.mtp'
                f.write(self.db_name)

        self.db = Data(self.db_name)


        filename = self.db_name.split('/')[-1]
        self.setWindowTitle(f"Monte Planer - {filename}")
        self.setMinimumSize(QSize(800, 800))
        self.tabs = Tabs(self)

        load_action = QAction('Wczytaj', self)
        load_action.triggered.connect(self.load_data)

        backup_action = QAction('Stwórz kopię zapasową', self)
        backup_action.triggered.connect(self.backup_data)

        menu = self.menuBar()
        file_menu = menu.addMenu('&Plik')
        file_menu.addActions([
            load_action,
            backup_action
        ])


        self.setCentralWidget(self.tabs)


    def load_data(self):
        db_name, _ = QFileDialog.getOpenFileName(self, 'Wczytaj dane', '', '*.mtp', '*.mtp')
        # self.path
        if not db_name:
            return
        self.db_name = db_name
        self.db = Data(self.db_name)
        self.tabs.load_data(self.db)
        with open('db_name', mode='w') as f:
            f.write(self.db_name)
        filename = self.db_name.split('/')[-1]
        self.setWindowTitle(f"Monte Planer - {filename}")
        return True
    
    def backup_data(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Stwórz kopię zapasową', f'{self.db_name[:-4]} - kopia zapasowa.mtp', '*.mtp', '*.mtp')
        if not path:
            return
        shutil.copy(self.db_name, path)
        return True


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
app.exec()