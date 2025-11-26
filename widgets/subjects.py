from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QHBoxLayout,\
      QFrame, QLabel, QDialogButtonBox, QMessageBox, QInputDialog, QGridLayout, QCheckBox, QSizePolicy
from PyQt5.QtCore import Qt

class SubjectsWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)
        self.data = data
        top_row = QHBoxLayout()
        layout= QVBoxLayout()

        self.class_list = QComboBox()
        self.class_list.addItems(self.data['classes'].keys())
        self.class_list.currentTextChanged.connect(self.load_class)
        top_row.addWidget(self.class_list)

        self.list = QComboBox(self)
        self.list.currentTextChanged.connect(self.load_subject)
        top_row.addWidget(self.list)
        layout.addLayout(top_row)

        
        self.frame = QFrame()
        frame_layout = QVBoxLayout()
        teacher_row = QHBoxLayout()
        teacher_row.addWidget(QLabel('Nauczyciel:'))
        self.teacher_list = QComboBox()
        teacher_row.addWidget(self.teacher_list)
        frame_layout.addLayout(teacher_row)
        self.frame.setLayout(frame_layout)

        self.student_list = QGridLayout()
        main_checkbox = QCheckBox()
        main_checkbox.toggled.connect(self.toggle_all_checkboxes)
        self.student_list.addWidget(QLabel("Uczniowie:"), 0, 0)
        self.student_list.addWidget(main_checkbox, 0, 1)
        self.student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        frame_layout.addLayout(self.student_list)

        layout.addWidget(self.frame)
        new_subject_btn_box = QDialogButtonBox()
        new_subject_btn = new_subject_btn_box.addButton('Dodaj Przedmiot', QDialogButtonBox.ButtonRole.ActionRole)
        new_subject_btn.clicked.connect(self.new_subject)
        layout.addWidget(new_subject_btn_box)
        self.setLayout(layout)

    def clear_students(self):
        for row in range(1, self.student_list.rowCount()):
            for col in  range(self.student_list.columnCount()):
                widget = self.student_list.itemAtPosition(row, col)
                if widget:
                    widget.widget().deleteLater()

    def load_class(self):
        class_name = self.class_list.currentText()
        if not class_name:
            return False
        
        # subjects
        self.list.clear()
        class_dict = self.data['classes'][class_name]
        subject_names = class_dict['subjects'].keys()
        if not subject_names:
            self.teacher_list.setCurrentText('')
        
        # students
        self.clear_students()
        
        for n, student in enumerate(class_dict['students'].keys()):
            #name
            name_label = QLabel(student)
            name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            self.student_list.addWidget(name_label, n+1, 0)
            #checkbox
            checkbox = QCheckBox()
            checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            checkbox.setObjectName(student)
            checkbox.toggled.connect(self.checkbox_clicked)
            self.student_list.addWidget(checkbox,n+1, 1)

        self.list.addItems(subject_names)

    def load_subject(self):
        subject_name = self.list.currentText()
        if not subject_name:
            return False
        class_name = self.class_list.currentText()
        subject = self.data['classes'][class_name]['subjects'][subject_name]
        # teacher
        teacher_name = subject['teacher']
        self.teacher_list.setCurrentText(teacher_name)
        # students
        for student, subjects in self.data['classes'][class_name]['students'].items():
            checkbox: QCheckBox = self.frame.findChildren(QCheckBox, student)[-1]
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(subject_name in subjects)
                checkbox.blockSignals(False)



    def new_subject(self):
        class_name = self.class_list.currentText()
        if not class_name:
            return False
        subject_name, ok = QInputDialog.getText(self, 'Dodaj Przedmiot', 'Przedmiot:')
        if ok and subject_name:
            if subject_name in self.data['classes'][class_name]['subjects'].keys():
                QMessageBox.warning(self, 'Uwaga', 'Taki przedmiot już istnieje')
            else:
                self.data['classes'][class_name]['subjects'][subject_name] = {'teacher': '', 'lengths': []}
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
        student = self.data['classes'][class_name]['students'][checkbox.objectName()]
        subject_name = self.list.currentText()
        if checkbox.isChecked() and subject_name not in student:
            student.append(subject_name)
        elif  subject_name in student: 
            student.remove(subject_name)


    def load_data(self, data):
        self.data = data
        self.teacher_list.clear()
        self.teacher_list.addItem('')
        self.teacher_list.addItems(self.data['teachers'].keys())
        self.class_list.clear()
        self.class_list.addItems(self.data['classes'].keys())


        
    