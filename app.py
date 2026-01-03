import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QMenu
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

import shutil
import os
import sys

from data import Data
from tabs import Tabs
from functions import get_user_data_dir




user_data_dir = get_user_data_dir('MontePlaner')
os.makedirs(user_data_dir, exist_ok=True)
db_name_path = os.path.join(user_data_dir, 'db_name')
basedir = os.path.dirname(__file__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        if not os.path.isfile(db_name_path):
            with open(db_name_path, 'x') as f:
                pass
        
        with open(db_name_path, 'r+') as f:
            self.db_name = f.read().strip()
            if not self.db_name:
                self.db_name = os.path.join(user_data_dir, 'planer.mtp')
                f.write(self.db_name)

        self.db = Data(self.db_name)


        filename = self.db_name.split('/')[-1]
        self.setWindowTitle(f"Monte Planer - {filename}")
        self.setWindowIcon(QIcon(os.path.join(basedir,'icon.png')))
        self.setMinimumSize(QSize(800, 800))
        self.tabs = Tabs(self)

        load_action = QAction('Wczytaj', self)
        load_action.triggered.connect(self.load_data)

        backup_action = QAction('Stwórz kopię zapasową', self)
        backup_action.triggered.connect(self.backup_data)

        export_action = QAction('&Eksportuj', self)
        export_action.triggered.connect(self.tabs.plan.export)
        

        menu = self.menuBar()
        file_menu = menu.addMenu('&Plik')
        file_menu.addActions([
            load_action,
            backup_action,
            export_action
        ])

        plan_menu = menu.addMenu('&Lekcje')
        clear_menu = plan_menu.addMenu('&Wyczyść')

        clear_unl_les_action = QAction('&Niezablokowane', self)
        clear_unl_les_action.triggered.connect(self.clear_unl_lessons)
        clear_all_les_action = QAction('&Wszystkie', self)
        clear_all_les_action.triggered.connect(self.clear_all_lessons)
        clear_menu.addActions([clear_unl_les_action, clear_all_les_action])

        color_lessons_action = QAction('&Uzupełnij plan', self)
        color_lessons_action.triggered.connect(self.color_lessons)
        lock_all_action = QAction('&Zablokuj wszystkie', self)
        lock_all_action.triggered.connect(self.lock_all_lessons)
        unlock_all_action = QAction('&Odblokuj wszystkie', self)
        unlock_all_action.triggered.connect(self.unlock_all_lessons)

        plan_menu.addActions([
            color_lessons_action,
            lock_all_action,
            unlock_all_action
        ])


        self.setCentralWidget(self.tabs)


    def load_data(self):
        db_name, _ = QFileDialog.getOpenFileName(self, 'Wczytaj dane', str(user_data_dir.absolute()), '*.mtp', '*.mtp')
        if not db_name:
            return
        self.db_name = db_name
        self.db = Data(self.db_name)
        self.tabs.load_data(self.db)
        with open(db_name_path, mode='w') as f:
            f.write(self.db_name)
        filename = self.db_name.split('/')[-1]
        self.setWindowTitle(f"Monte Planer - {filename}")
        return True
    
    def backup_data(self):
        directory = os.path.join(user_data_dir, f'{self.db_name[:-4]} - kopia zapasowa.mtp')
        path, _ = QFileDialog.getSaveFileName(self, 'Stwórz kopię zapasową', directory, '*.mtp', '*.mtp')
        if not path:
            return
        shutil.copy(self.db_name, path)
        return True
    
    def export(self):
        self.tabs.plan.export
    
    def clear_unl_lessons(self):
        self.db.clear_all_lesson_blocks(leave_locked=True)
        self.tabs.refresh()

    def clear_all_lessons(self):
        self.db.clear_all_lesson_blocks()
        self.tabs.refresh()

    def color_lessons(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.tabs.plan.dfeas()
        self.tabs.refresh()
        QApplication.restoreOverrideCursor()

    def lock_all_lessons(self):
        self.db.set_all_lessons_locked()
        self.tabs.refresh()

    def unlock_all_lessons(self):
        self.db.set_all_lessons_locked(False)
        self.tabs.refresh()


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
app.exec()