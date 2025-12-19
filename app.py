import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction
from PyQt5.QtCore import QSize
from struct import pack

import json

from data import Data, Teacher
from widgets.tabs import Tabs

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = ''#blank_data()
        self.db = Data()

        self.save_path = ''

        self.setWindowTitle("Monte Planer")
        self.setMinimumSize(QSize(800, 800))
        self.tabs = Tabs(self, self.data)

        save_action = QAction('Zapisz', self)
        save_action.triggered.connect(self.save_data)

        save_as_action = QAction('Zapisz jako', self)
        save_as_action.triggered.connect(self.save_as_data)

        load_action = QAction('Wczytaj', self)
        load_action.triggered.connect(self.load_data)


        menu = self.menuBar()
        file_menu = menu.addMenu('&Plik')
        file_menu.addActions([
            save_action,
            save_as_action,
            load_action,
        ])


        self.setCentralWidget(self.tabs)


    def save_data(self):
        if self.save_path:
            data_json = json.dumps(self.data)
            with open(self.save_path, 'w') as save_file:
                save_file.write(data_json)
        else:
            self.save_as_data()


    def save_as_data(self):
        data_json = json.dumps(self.data)
        self.save_path, _ = QFileDialog.getSaveFileName(self, "Zapisz dane", 'data.mtp', "Dane programu (*.mtp)")
        if not self.save_path:
            return
        with open(self.save_path, 'w') as save_file:
            save_file.write(data_json)


    def load_data(self):
        open_path, _ = QFileDialog.getOpenFileName(self, 'Wczytaj dane', '', '*.mtp', '*.mtp')
        if not open_path:
            return
        self.save_path = open_path
        with open(open_path, 'r') as open_file:
            self.data = json.load(open_file)
            self.tabs.load_data(self.data)
        return True

app = QApplication(sys.argv)
# print(open_connection())
window = MainWindow()
window.showMaximized()
app.exec()