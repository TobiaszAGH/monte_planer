from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QDialog, QDialogButtonBox, \
      QPushButton, QLabel, QDialogButtonBox, QMessageBox, QInputDialog, QGridLayout, QCheckBox, QSizePolicy
from PyQt5.QtCore import Qt

from data import Data, Class, Subclass, Student, Subject

class AddLessonDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('Podaj długość')
        layout = QVBoxLayout(self)
        self.combobox = QComboBox()
        layout.addWidget(self.combobox)
        self.combobox.addItems(['30', '45', '60', '90'])
        self.combobox.setEditable(True)
        buttonBox = QDialogButtonBox()
        layout.addWidget(buttonBox)
        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

class SubjectsWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)
        self.data = data
        self.db: Data = parent.db
        layout= QVBoxLayout()
        self.setLayout(layout)

        top_row = QHBoxLayout()
        layout.addLayout(top_row)

        # classes
        self.class_list = QComboBox()
        for my_class in self.db.all_classes():
            self.class_list.addItem(my_class.name, my_class)
        self.class_list.currentTextChanged.connect(self.load_type_list)
        top_row.addWidget(self.class_list)

        # subject type
        self.type_list = QComboBox()
        self.type_list.currentTextChanged.connect(self.load_class)
        top_row.addWidget(self.type_list)

        # subject
        self.list = QComboBox(self)
        self.list.currentTextChanged.connect(self.load_subject)
        top_row.addWidget(self.list)

        # container to preserve layout
        self.container = QWidget()
        container_layout = QVBoxLayout()
        self.container.setLayout(container_layout)
        layout.addWidget(self.container)

        # frame to hide content when no info available
        self.frame = QWidget()
        self.frame_layout = QVBoxLayout()
        self.frame.setLayout(self.frame_layout)
        container_layout.addWidget(self.frame)

        # subject info row
        teacher_row = QHBoxLayout()
        self.frame_layout.addLayout(teacher_row)
        teacher_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # teachers
        teacher_row.addWidget(QLabel('Nauczyciel:'))
        self.teacher_list = QComboBox()
        self.teacher_list.currentTextChanged.connect(self.setTeacher)
        teacher_row.addWidget(self.teacher_list)
        
        # lessons
        teacher_row.addWidget(QLabel('Lekcje:'))
        self.lessons = QHBoxLayout()
        self.lessons.setAlignment(Qt.AlignmentFlag.AlignLeft)
        teacher_row.addLayout(self.lessons)
        add_lesson_btn = QPushButton('+')
        add_lesson_btn.clicked.connect(self.add_lesson)
        teacher_row.addWidget(add_lesson_btn)

        self.student_list = QGridLayout()
        main_checkbox = QCheckBox()
        main_checkbox.toggled.connect(self.toggle_all_checkboxes)
        # main_checkbox.student = 'dupa'
        self.student_list.addWidget(QLabel("Uczniowie:"), 0, 0)
        self.student_list.addWidget(main_checkbox, 0, 1)
        self.student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.frame_layout.addLayout(self.student_list)

        # bottom row
        new_subject_btn_box = QDialogButtonBox()
        new_subject_btn = new_subject_btn_box.addButton('Dodaj przedmiot', QDialogButtonBox.ButtonRole.ActionRole)
        new_subject_btn.clicked.connect(self.new_subject)
        remove_subject_btn = new_subject_btn_box.addButton('Usuń przedmiot', QDialogButtonBox.ButtonRole.ActionRole)
        remove_subject_btn.clicked.connect(self.remove_subject)
        layout.addWidget(new_subject_btn_box)

        # self.student_list = QGridLayout()

        self.load_class()
        self.frame.hide()

    def clear_students(self):
        for row in range(1, self.student_list.rowCount()):
            for col in  range(self.student_list.columnCount()):
                widget = self.student_list.itemAtPosition(row, col)
                if widget:
                    widget.widget().deleteLater()

    def load_type_list(self):
        my_class: Class = self.class_list.currentData()
        if not my_class:
            return False
        self.type_list.clear()
        subclass: Subclass
        for subclass in my_class.subclasses:
            self.type_list.addItem(subclass.name.upper(), subclass)
        self.type_list.addItem('Rozszerzone', subclass.my_class)


    def load_class(self):
        my_class = self.type_list.currentData()
        if not my_class:
            return False
        
        # subjects
        self.list.clear()
        if not self.type_list.currentText():
            return False
        for subject in my_class.subjects:
            self.list.addItem(subject.name, subject)
        
        # students
        self.clear_students()
        students = my_class.students
        students.sort(key=lambda x: x.name)
        student: Student
        for student in students:
            # print(student.name)
            n = self.student_list.rowCount()
            #name
            name_label = QLabel(student.name)
            name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            self.student_list.addWidget(name_label, n+1, 0)
            #checkbox
            checkbox = QCheckBox()
            checkbox.student = student
            checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            checkbox.toggled.connect(self.checkbox_clicked)
            self.student_list.addWidget(checkbox,n+1, 1)
        
        self.load_subject()


    def load_subject(self):
        subject: Subject = self.list.currentData()
        if not subject:
            self.frame.hide()
            return False
        else:
            self.frame.show()

        # teacher
        teacher = subject.teacher
        teacher_name = teacher.name if teacher else ''
        self.teacher_list.setCurrentText(teacher_name)
        # lessons
        for n in range(self.lessons.count()):
            self.lessons.itemAt(n).widget().deleteLater()
        for lesson in subject.lessons:
            btn = QPushButton(str(lesson.length))
            btn.lesson = lesson
            self.lessons.addWidget(btn)
            btn.clicked.connect(self.remove_lesson)
        # students
        for checkbox in self.frame.findChildren(QCheckBox):
            if hasattr(checkbox, 'student'):
                checkbox.blockSignals(True)
                checkbox.setChecked(subject in checkbox.student.subjects)
                checkbox.blockSignals(False)



    def new_subject(self):
        my_class = self.type_list.currentData()
        if not my_class:
            return False
        
        subject_name, ok = QInputDialog.getText(self, 'Dodaj Przedmiot', 'Przedmiot:')
        if ok and subject_name:
            basic = type(my_class) == Subclass
            subject = self.db.create_subject(subject_name, basic, my_class)
            self.list.addItem(subject.name, subject)
            self.list.setCurrentText(subject.name)


    def toggle_all_checkboxes(self):
        checkboxes: list[QCheckBox] = self.frame.findChildren(QCheckBox)
        new_state = checkboxes[0].isChecked()
        for chechbox in checkboxes:
            chechbox.setChecked(new_state)


    def checkbox_clicked(self):
        checkbox:QCheckBox = self.sender()
        subject = self.list.currentData()
        student = checkbox.student
        if checkbox.isChecked():
            self.db.add_subject_to_student(subject, student)
        else:
            self.db.remove_subject_from_student(subject, student)


    def setTeacher(self):
        teacher = self.teacher_list.currentData()
        subject = self.list.currentData()
        if not (subject and teacher):
            return False
        self.db.update_subject_teacher(subject, teacher)

    def add_lesson(self):
        dialog = AddLessonDialog(self)
        ok = dialog.exec()
        if not ok:
            return False
        length = dialog.combobox.currentText()
        try:
            length = int(length)
        except:
            QMessageBox.warning(self, 'Błąd', 'Podaj liczbę!')
            return False
        subject: Subject = self.list.currentData()
        lesson = self.db.create_lessson(length, subject)
        btn = QPushButton(str(length))
        btn.lesson = lesson
        self.lessons.addWidget(btn)
        btn.clicked.connect(self.remove_lesson)

    def remove_lesson(self):
        btn: QPushButton = self.sender()
        self.db.delete_lesson(btn.lesson)
        btn.deleteLater()

    def remove_subject(self):
        subject = self.list.currentData()
        message = f'Czy na pewno chcesz usunąć: {subject.name}'
        if QMessageBox.question(self, 'Uwaga', message) != QMessageBox.StandardButton.Yes:
                return False
        self.db.delete_subject(subject)
        self.load_data(self.data)



    def load_data(self, data):
        self.data = data
        self.teacher_list.clear()
        self.teacher_list.addItem('')
        for t in self.db.read_all_teachers():
            self.teacher_list.addItem(t.name, t)
        self.class_list.clear()
        for my_class in self.db.all_classes():
            self.class_list.addItem(my_class.name, my_class)

        self.load_subject()


        
    