from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QCursor
from data import Data
from db_config import settings


class ManageClassroomsDialog(QDialog):
    def __init__(self, parent_block):
        super().__init__()

        self.setWindowTitle('Zarządzaj salami')
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.db: 'Data' = parent_block.db
        self.block = parent_block.block
        self.lessons = self.block.lessons



        for n, lesson in enumerate(self.lessons):
            label = QLabel(lesson.subject.full_name(True))
            self.main_layout.addWidget(label, n, 0)
            combobox = QComboBox()
            combobox.lesson = lesson
            combobox.currentTextChanged.connect(self.update_lesson_classroom(lesson))
            self.update_classroom_list(combobox)
            self.main_layout.addWidget(combobox,n , 1) 

        buttonBox = QDialogButtonBox()
        self.main_layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        # buttonBox.rejected.connect(self.reject)
        self.move(QCursor.pos() + QPoint(10,10))

    def update_lesson_classroom(self, lesson):
        def func():
            classroom = self.sender().currentData()
            self.db.update_lesson_classroom(lesson, classroom)
            for i in range(len(self.lessons)):
                combobox = self.main_layout.itemAt(i*2+1).widget()
                self.update_classroom_list(combobox)
        
        return func
    
    def update_classroom_list(self, list: QComboBox):
        lesson = list.lesson
        list.blockSignals(True)
        list.clear()
        for i, classroom in enumerate(self.db.all_classrooms()):
            list.addItem(classroom.name, classroom)
            collisions = '\n'.join(self.db.classroom_collisions(classroom, self.block, lesson))
            if collisions:
                list.setItemData(i, collisions, Qt.ToolTipRole)
                if not settings.allow_creating_conflicts:
                    list.setItemData(i, 0, Qt.UserRole - 1)
                else:
                    list.setItemData(i, QColor('red'), Qt.BackgroundRole)
        list.insertItem(0, '')
        if lesson.classroom:
            list.setCurrentText(lesson.classroom.name)
        else:
            list.setCurrentIndex(0)
        list.blockSignals(False)
            
            



