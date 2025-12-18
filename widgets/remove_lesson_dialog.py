from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox
from data import Subclass, Class, Subject, Lesson


class RemoveLessonFromBlockDialog(QDialog):
    def __init__(self, block):
        super().__init__()

        self.setWindowTitle('Wybierz przedmiot')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list = QComboBox()
        layout.addWidget(self.list)

        lessons = block.lessons
        for lesson in lessons:
            self.list.addItem(lesson.subject.name, lesson) 

        buttonBox = QDialogButtonBox()
        layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



