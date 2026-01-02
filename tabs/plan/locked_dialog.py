from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QCheckBox
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QCursor
from data import Data


class ManageLockedDialog(QDialog):
    def __init__(self, parent_block):
        super().__init__()
        

        self.setWindowTitle('Blokowanie lekcji')
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.db: 'Data' = parent_block.db
        self.block = parent_block.block
        self.lessons = self.block.lessons



        for lesson in self.lessons:
            checkbox = QCheckBox(lesson.subject.get_name(), self)
            self.main_layout.addWidget(checkbox)
            checkbox.setChecked(lesson.block_locked)
            checkbox.clicked.connect(self.update_lesson_locked(lesson))

        buttonBox = QDialogButtonBox()
        self.main_layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        # buttonBox.rejected.connect(self.reject)

        self.move(QCursor.pos() + QPoint(10,10))

    def update_lesson_locked(self, lesson):
        def func():
            locked = self.sender().isChecked()
            self.db.update_lesson_locked(lesson, locked)
        return func
   



