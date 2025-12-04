from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QDialog, QDialogButtonBox, \
      QPushButton, QLabel, QDialogButtonBox, QMessageBox, QInputDialog, QGridLayout, QCheckBox, QSizePolicy
from PyQt5.QtCore import Qt

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
        layout= QVBoxLayout()
        self.setLayout(layout)

        top_row = QHBoxLayout()
        layout.addLayout(top_row)

        # classes
        self.class_list = QComboBox()
        self.class_list.addItems(self.data['classes'].keys())
        self.class_list.currentTextChanged.connect(self.load_type_list)
        top_row.addWidget(self.class_list)

        # subject type
        self.type_list = QComboBox()
        # self.class_list.addItems(self.data['classes'][])
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
        frame_layout = QVBoxLayout()
        self.frame.setLayout(frame_layout)
        container_layout.addWidget(self.frame)

        # subject info row
        teacher_row = QHBoxLayout()
        frame_layout.addLayout(teacher_row)
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

        # list of students
        self.student_list = QGridLayout()
        main_checkbox = QCheckBox()
        main_checkbox.toggled.connect(self.toggle_all_checkboxes)
        self.student_list.addWidget(QLabel("Uczniowie:"), 0, 0)
        self.student_list.addWidget(main_checkbox, 0, 1)
        self.student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        frame_layout.addLayout(self.student_list)

        # bottom row
        new_subject_btn_box = QDialogButtonBox()
        new_subject_btn = new_subject_btn_box.addButton('Dodaj przedmiot', QDialogButtonBox.ButtonRole.ActionRole)
        new_subject_btn.clicked.connect(self.new_subject)
        remove_subject_btn = new_subject_btn_box.addButton('Usuń przedmiot', QDialogButtonBox.ButtonRole.ActionRole)
        remove_subject_btn.clicked.connect(self.remove_subject)
        layout.addWidget(new_subject_btn_box)

        self.frame.hide()

    def clear_students(self):
        for row in range(1, self.student_list.rowCount()):
            for col in  range(self.student_list.columnCount()):
                widget = self.student_list.itemAtPosition(row, col)
                if widget:
                    widget.widget().deleteLater()

    def load_type_list(self):
        class_name = self.class_list.currentText()
        if not class_name:
            return False
        self.type_list.clear()
        items = list(self.data['classes'][class_name]['subjects'].keys())
        items.sort()
        self.type_list.addItems(items)

    def load_class(self):
        class_name = self.class_list.currentText()
        if not class_name:
            return False
        
        # subjects
        self.list.clear()
        class_dict = self.data['classes'][class_name]
        subject_type = self.type_list.currentText()
        if not subject_type:
            return False
        subject_names = list(class_dict['subjects'][subject_type].keys())
        subject_names.sort()
        if not subject_names:
            self.teacher_list.setCurrentText('')
        
        # students
        self.clear_students()
        if subject_type == 'extra':
            subclasses = list(class_dict['students'].keys())
        else:
            subclasses = [subject_type]
        
        for subclass in subclasses:
            for student in class_dict['students'][subclass].keys():
                n = self.student_list.rowCount()
                #name
                name_label = QLabel(student)
                name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
                self.student_list.addWidget(name_label, n+1, 0)
                #checkbox
                checkbox = QCheckBox()
                checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
                checkbox.setObjectName(f'{subclass};{student}')
                checkbox.toggled.connect(self.checkbox_clicked)
                self.student_list.addWidget(checkbox,n+1, 1)

        self.list.addItems(subject_names)

    def load_subject(self):
        subject_name = self.list.currentText()
        subject_type = self.type_list.currentText()
        if not (subject_name and subject_type):
            self.frame.hide()
            return False
        else:
            self.frame.show()
        class_name = self.class_list.currentText()
        subject = self.data['classes'][class_name]['subjects'][subject_type][subject_name]
        # teacher
        teacher_name = subject['teacher']
        self.teacher_list.setCurrentText(teacher_name)
        # lessons
        for n in range(self.lessons.count()):
            self.lessons.itemAt(n).widget().deleteLater()
        for lesson in subject['lengths']:
            btn = QPushButton(str(lesson))
            self.lessons.addWidget(btn)
            btn.clicked.connect(self.remove_lesson)
        # students
        for subclass in self.data['classes'][class_name]['students'].keys():
            for student, subjects in self.data['classes'][class_name]['students'][subclass].items():
                checkbox: QCheckBox = self.frame.findChildren(QCheckBox, f'{subclass};{student}')
                if checkbox:
                    checkbox = checkbox[-1]
                    checkbox.blockSignals(True)
                    checkbox.setChecked(subject_name in subjects[subject_type])
                    checkbox.blockSignals(False)



    def new_subject(self):
        class_name = self.class_list.currentText()
        subject_type = self.type_list.currentText()
        if not class_name:
            return False
        subject_name, ok = QInputDialog.getText(self, 'Dodaj Przedmiot', 'Przedmiot:')
        if ok and subject_name:
            if subject_name in self.data['classes'][class_name]['subjects'][subject_type].keys():
                QMessageBox.warning(self, 'Uwaga', 'Taki przedmiot już istnieje')
            else:
                self.data['classes'][class_name]['subjects'][subject_type][subject_name] = {'teacher': '', 'lengths': []}
                self.list.addItem(subject_name)
                self.list.setCurrentText(subject_name)


    def toggle_all_checkboxes(self):
        checkboxes: list[QCheckBox] = self.frame.findChildren(QCheckBox)
        new_state = checkboxes[0].isChecked()
        for chechbox in checkboxes:
            chechbox.setChecked(new_state)


    def checkbox_clicked(self):
        checkbox = self.sender()
        class_name = self.class_list.currentText()
        subclass, student_name = checkbox.objectName().split(';')
        student = self.data['classes'][class_name]['students'][subclass][student_name]
        subject_name = self.list.currentText()
        subject_type = self.type_list.currentText()
        if checkbox.isChecked() and subject_name not in student[subject_type]:
            student[subject_type].append(subject_name)
        elif subject_name in student[subject_type]: 
            student[subject_type].remove(subject_name)


    def setTeacher(self):
        teacher_name = self.teacher_list.currentText()
        if not teacher_name:
            return False
        class_name = self.class_list.currentText()
        subject_name = self.list.currentText()
        subject_type = self.type_list.currentText()
        self.data['classes'][class_name]['subjects'][subject_type][subject_name]['teacher'] = teacher_name

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
        btn = QPushButton(str(length))
        self.lessons.addWidget(btn)
        btn.clicked.connect(self.remove_lesson)
        class_name = self.class_list.currentText()
        subject_name = self.list.currentText()
        subject_type = self.type_list.currentText()
        self.data['classes'][class_name]['subjects'][subject_type][subject_name]['lengths'].append(length)

    def remove_lesson(self):
        btn: QPushButton = self.sender()
        length = int(btn.text())
        class_name = self.class_list.currentText()
        subject_name = self.list.currentText()
        subject_type = self.type_list.currentText()
        self.data['classes'][class_name]['subjects'][subject_type][subject_name]['lengths'].remove(length)
        btn.deleteLater()

    def remove_subject(self):
        class_name = self.class_list.currentText()
        subject_name = self.list.currentText()
        subject_type = self.type_list.currentText()
        message = f'Czy na pewno chcesz usunąć: {subject_name}'
        if QMessageBox.question(self, 'Uwaga', message) != QMessageBox.StandardButton.Yes:
                return False
        self.data['classes'][class_name]['subjects'][subject_type].pop(subject_name)
        checkboxes = [chb for chb in self.findChildren(QCheckBox)[1:] if chb.isChecked()]
        for checkbox in checkboxes:
            subclass, student_name = checkbox.objectName().split(';')
            self.data['classes'][class_name]['students'][subclass][student_name][subject_type].remove(subject_name)
        self.load_data(self.data)



    def load_data(self, data):
        self.data = data
        self.teacher_list.clear()
        self.teacher_list.addItem('')
        teacher_names = list(self.data['teachers'].keys())
        teacher_names.sort()
        self.teacher_list.addItems(teacher_names)
        self.class_list.clear()
        class_names = list(self.data['classes'].keys())
        class_names.sort()
        self.class_list.addItems(class_names)


        
    