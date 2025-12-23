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
        none_viable = True
        select_next = False
        for i, subject in enumerate(subjects):
            self.subject_list.addItem(subject.name, subject)
            collisions = [
                f'{subject.teacher.name} prowadzi {l.name_and_time()}'
                for l in self.db.get_collisions_for_teacher_at_block(subject.teacher, self.block)
            ]
            collisions.extend([
                f'Niektórzy uczniowie mają {l.name_and_time()}'
                for l in self.db.get_collisions_for_students_at_block(subject.students, self.block)
            ])
            if subject.teacher and not self.db.is_teacher_available(subject.teacher, self.block):
                collisions.append(f'{subject.teacher.name} nie jest dostępny w tych godzinach.')
            collisions = '\n'.join(collisions)
            if collisions:
                if self.subject_list.currentIndex() == i and i < self.subject_list.count():
                    select_next = True
                self.subject_list.setItemData(i, collisions, Qt.ToolTipRole)
                if not settings.allow_creating_conflicts:
                    self.subject_list.setItemData(i, 0, Qt.UserRole - 1)
                else:
                    self.subject_list.setItemData(i, QColor('red'), Qt.BackgroundRole)
            else:
                none_viable = False
                if select_next:
                    self.subject_list.setCurrentIndex(i)
                    select_next = False
        if none_viable:
            self.subject_list.setCurrentIndex(-1)


    def update_lesson_list(self):
        subject: Subject = self.subject_list.currentData()
        lesson: Lesson
        self.lesson_list.clear()
        none_viable = True
        if not subject:
            return False
        for i, lesson in enumerate(subject.lessons):
            if lesson.block:
                self.lesson_list.addItem(f'{str(lesson.length)} ({days[lesson.block.day]} {lesson.block.print_time()})', lesson)
            else:
                self.lesson_list.addItem(str(lesson.length), lesson)
            if lesson.length > self.block.length*5:
                self.lesson_list.setItemData(i, f'Ten blok trwa tylko {self.block.length*5} minut', Qt.ToolTipRole)
                if not settings.allow_creating_conflicts:
                    self.lesson_list.setItemData(i, 0, Qt.UserRole - 1)
            else:
                none_viable = False
        if none_viable:
            self.lesson_list.setCurrentIndex(-1)

    def update_classroom_list(self):
        self.classroom_list.clear()
        # subject = self.subject_list.currentData(Qt.UserRole)
        lesson = self.lesson_list.currentData()
        if not lesson:
            return
        none_viable = True
        select_next = False
        for i, classroom in enumerate(self.db.all_classrooms()):
            self.classroom_list.addItem(classroom.name, classroom)

            collisions = self.db.classroom_collisions(classroom, self.block, lesson)

            collisions = '\n'.join(collisions)
            if collisions:
                if self.classroom_list.currentIndex() == i and i < self.classroom_list.count():
                    select_next = True
                self.classroom_list.setItemData(i, collisions, Qt.ToolTipRole)
                if not settings.allow_creating_conflicts:
                    self.classroom_list.setItemData(i, 0, Qt.UserRole - 1)
                else:
                    self.classroom_list.setItemData(i, QColor('red'), Qt.BackgroundRole)
            else:
                none_viable = False
                if select_next:
                    self.classroom_list.setCurrentIndex(i)
                    select_next = False
        if none_viable:
            self.classroom_list.setCurrentIndex(-1)


