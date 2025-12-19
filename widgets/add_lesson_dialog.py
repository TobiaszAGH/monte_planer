from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox
from data import Subclass, Subject, Lesson, days


class AddLessonToBlockDialog(QDialog):
    def __init__(self, parent, subclass: Subclass):
        super().__init__()
        self.db = parent.db
        self.subclass: Subclass = subclass
        

        self.setWindowTitle('Wybierz przedmiot')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.type_list = QComboBox()
        layout.addWidget(self.type_list)



        if isinstance(self.subclass, Subclass):
            self.type_list.addItem('Przedmiot podstawowy')
            self.type_list.setItemData(0, self.subclass)
        else:
            self.type_list.addItem('Poziom rozszerzony', self.subclass)
            for subclass in self.subclass.subclasses:
                self.type_list.addItem(f'Poziom podstawowy - {subclass.full_name()}', subclass)
        self.type_list.currentTextChanged.connect(self.update_subject_list)

        self.subject_list = QComboBox()
        layout.addWidget(self.subject_list)
        self.subject_list.currentTextChanged.connect(self.update_lesson_list)
        # self.update_subject_list()

        self.lesson_list = QComboBox()
        layout.addWidget(self.lesson_list)

        buttonBox = QDialogButtonBox()
        layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.update_subject_list()

    def update_subject_list(self):
        sub_class = self.type_list.currentData()
        subjects = sub_class.subjects
        self.subject_list.clear()
        for subject in subjects:
            self.subject_list.addItem(subject.name, subject) 

    def update_lesson_list(self):
        subject: Subject = self.subject_list.currentData()
        lesson: Lesson
        self.lesson_list.clear()
        if not subject:
            return False
        for lesson in subject.lessons:
            if lesson.block:
                self.lesson_list.addItem(f'{str(lesson.length)} ({days[lesson.block.day]} {lesson.block.print_time()})', lesson)
            else:
                self.lesson_list.addItem(str(lesson.length), lesson)

