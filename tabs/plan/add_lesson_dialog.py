from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from data import Subclass, Subject, Lesson, days, Data, LessonBlockDB
from db_config import settings

enabled_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

class AddLessonToBlockDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.db: Data = parent.db
        self.subclass: Subclass = parent.block.parent()
        self.block = parent.block
        

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
            for block in self.subclass.subclasses:
                self.type_list.addItem(f'Poziom podstawowy - {block.full_name()}', block)
        self.type_list.currentTextChanged.connect(self.update_subject_list)

        self.subject_list = QComboBox()
        layout.addWidget(self.subject_list)
        self.subject_list.currentTextChanged.connect(self.update_lesson_list)
        # self.update_subject_list()

        self.lesson_list = QComboBox()
        layout.addWidget(self.lesson_list)
        self.lesson_list.currentTextChanged.connect(self.update_classroom_list)

        self.classroom_list = QComboBox()
        layout.addWidget(self.classroom_list)
        self.classroom_list.addItem('')
        for classroom in self.db.all_classrooms():
            self.classroom_list.addItem(classroom.name, classroom)

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

    def update_classroom_list(self):
        for i in range(self.classroom_list.count()):
            self.classroom_list.setItemData(i, enabled_flags, Qt.UserRole - 1)
            self.classroom_list.setItemData(i, '', Qt.ToolTipRole)
            classroom = self.classroom_list.itemData(i, Qt.UserRole)
            if not classroom:
                continue
            # classroom used in other lessons
            collisions = self.db.possible_collisions_for_classroom_at_block(classroom, self.block)
            collisions = [l.name_and_time() for l in collisions]         # collisions = '\n'
            # classroom to small
            subject = self.subject_list.currentData(Qt.UserRole)
            if classroom.capacity < len(subject.students):
                collisions.append('Sala jest za mała.')
            collisions = '\n'.join(collisions)
            if collisions:
                self.classroom_list.setItemData(i, collisions, Qt.ToolTipRole)
                if not settings.allow_creating_conflicts:
                    self.classroom_list.setItemData(i, 0, Qt.UserRole - 1)
                else:
                    self.classroom_list.setItemData(i, QColor('red'), Qt.BackgroundRole)


