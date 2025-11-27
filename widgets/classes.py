from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, \
    QComboBox, QMessageBox, QVBoxLayout, QCheckBox, QGridLayout, QLabel, QStackedLayout, QSizePolicy, \
    QLineEdit

from PyQt5.QtCore import Qt

class ClassesWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)
        self.data = data

        main_layout = QVBoxLayout()

        layout= QHBoxLayout()
        self.list = QComboBox(self)
        self.list.addItems(data['classes'].keys())
        self.list.currentTextChanged.connect(self.populate_student_list)
        layout.addWidget(self.list)

        self.btn = QPushButton('Dodaj klasę')
        self.btn.clicked.connect(self.new_class)
        layout.addWidget(self.btn)

        main_layout.addLayout(layout)

        student_list_area = QWidget()
        self.student_list_area_layout = QStackedLayout()
        student_list_area.setLayout(self.student_list_area_layout)
        
        main_layout.addWidget(student_list_area)
        
        bottom_button_group = QHBoxLayout()
        new_name = QLineEdit()
        new_name.setPlaceholderText('Imię i nazwisko')
        bottom_button_group.addWidget(new_name)
        add_student_btn = QPushButton("Dodaj Ucznia")
        add_student_btn.clicked.connect(self.new_student)
        bottom_button_group.addWidget(add_student_btn)
        delete_student_button = QPushButton("Usuń")
        delete_student_button.clicked.connect(self.remove_students)
        bottom_button_group.addWidget(delete_student_button)
        add_subject_to_student_btn = QPushButton("Dodaj rozszerzenie")
        bottom_button_group.addWidget(add_subject_to_student_btn)

        main_layout.addLayout(bottom_button_group)


        self.setLayout(main_layout)

    def new_class(self):
        class_name, ok = QInputDialog.getText(self, 'Dodaj Klasę', 'Klasa:')
        if ok and class_name:
            if class_name in self.data['classes'].keys():
                QMessageBox.warning(self, 'Uwaga', 'Taka klasa już istnieje')
            else:
                self.data['classes'][class_name] = {'subjects': {}, 'students': {}}
                self.list.addItem(class_name)

    def load_data(self, data):
        #class selection
        self.data = data
        self.list.clear()
        self.list.addItems(self.data['classes'].keys())

        #clear widget
        for i in range(self.student_list_area_layout.count()):
            self.student_list_area_layout.itemAt(i).widget().deleteLater()
        
        #classes data
        for students in data['classes'].values():
            students = students['students']
            student_list = QGridLayout()
            student_list.setObjectName('student_list')
            student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            #headers
            main_checkbox = QCheckBox()
            main_checkbox.toggled.connect(self.toggle_all_checkboxes)
            student_list.addWidget(main_checkbox, 0, 0)
            student_list.addWidget(QLabel("Uczeń"), 0, 1)
            student_list.addWidget(QLabel("Rozszerzenia"), 0, 2)

            #load students
            for student in students.items():
                self.add_student_to_list(student, student_list)

            student_list_widget = QWidget()
            student_list_widget.setLayout(student_list)
            self.student_list_area_layout.addWidget(student_list_widget)

        self.student_list_area_layout.setCurrentIndex(0)

        
    def populate_student_list(self):
        selected_class = self.list.currentIndex()
        self.student_list_area_layout.setCurrentIndex(selected_class)

    def del_btn(self):
        btn = self.sender()
        student_name = btn.objectName()
        class_name = self.list.currentText()
        self.data['classes'][class_name]['students'][student_name].remove(btn.text())
        btn.deleteLater()

    def add_student_to_list(self, student, student_list: QGridLayout): 
        n = student_list.rowCount()
        student_name, subjects = student
        #checkbox
        checkbox = QCheckBox()
        checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        student_list.addWidget(checkbox,n, 0)
        #name
        name_label = QLabel(student_name)
        name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        student_list.addWidget(name_label, n, 1)
        #subjects
        subject_list = QHBoxLayout()
        # subject_list.setAlignment(Qt.AlignmentFlag.A)
        for subject in subjects:
            btn = QPushButton(subject)
            btn.setObjectName(student_name)
            subject_list.addWidget(btn)
            btn.clicked.connect(self.del_btn)
        subject_list.addStretch()
        student_list.addLayout(subject_list, n, 2)

    def new_student(self):
        new_name:QLineEdit = self.findChild(QLineEdit)
        new_name = new_name.text()
        if new_name:        
            curr_widget = self.student_list_area_layout.currentWidget()
            student_list:QWidget = curr_widget.findChild(QGridLayout)
            self.add_student_to_list((new_name, []), student_list)
            self.data['classes'][self.list.currentText()]['students'][new_name] = []

    def toggle_all_checkboxes(self):
        curr_widget:QWidget = self.student_list_area_layout.currentWidget()
        checkboxes: list[QCheckBox] = curr_widget.findChildren(QCheckBox)
        new_state = checkboxes[0].isChecked()
        for chechbox in checkboxes:
            chechbox.setChecked(new_state)

    def remove_students(self):
        curr_widget = self.student_list_area_layout.currentWidget()
        student_list:QGridLayout = curr_widget.findChild(QGridLayout)
        checkboxes:list[QCheckBox] = curr_widget.findChildren(QCheckBox)
        to_remove = []
        for checkbox in checkboxes[1:]:
            if checkbox.isChecked():
                index = student_list.indexOf(checkbox)
                label:QLabel = student_list.itemAt(index+1).widget()
                student_name = label.text()
                self.data['classes'][self.list.currentText()]['students'].pop(student_name)
                to_remove.append(student_list.indexOf(label))
        
        amount = len(to_remove)
        if amount == 0:
            return False
        message = f"Czy na pewno chcesz usunąć {amount} {'ucznia' if amount==1 else 'uczniów'}?"
        ok = QMessageBox.question(self, 'Uwaga', message)
        if not ok:
            return False

        for i in to_remove[::-1]:
            for n in range(i-1, i+2):
                item = student_list.itemAt(n)
                if item.widget():
                    item.widget().deleteLater()
                layout = item.layout()
                if layout:
                    for j in range(layout.count()-1):
                       layout.itemAt(j).widget().deleteLater()
                    
                

