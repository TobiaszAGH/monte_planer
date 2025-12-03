from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, \
    QComboBox, QMessageBox, QVBoxLayout, QCheckBox, QGridLayout, QLabel, QStackedLayout, QSizePolicy, \
    QLineEdit, QScrollArea, QSpacerItem, QDialog, QDialogButtonBox

from PyQt5.QtCore import Qt

from string import ascii_lowercase

class AddSubjectDialog(QDialog):
    def __init__(self, parent, class_name, subclass, data):
        super().__init__(parent)
        self.data = data
        self.class_name = class_name

        self.setWindowTitle('Wybierz przedmiot')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.type_list = QComboBox()
        layout.addWidget(self.type_list)
        self.type_list.addItems(['Przedmiot podstawowy', 'Przedmiot rozszerzony'])
        self.type_list.setItemData(0, subclass)
        self.type_list.setItemData(1, 'extra')
        self.type_list.currentTextChanged.connect(self.update_subject_list)

        self.subject_list = QComboBox()
        layout.addWidget(self.subject_list)
        self.update_subject_list()

        buttonBox = QDialogButtonBox()
        layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def update_subject_list(self):
        subject_names = self.data['classes'][self.class_name]['subjects'][self.type_list.currentData()].keys()
        self.subject_list.clear()
        self.subject_list.addItems(subject_names)
        

class ClassesWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)
        self.data = data

        main_layout = QVBoxLayout()

        layout= QHBoxLayout()
        self.list = QComboBox(self)
        self.list.addItems(data['classes'].keys())
        self.list.currentTextChanged.connect(self.load_class)
        layout.addWidget(self.list)

        btn = QPushButton('Dodaj klasę')
        btn.clicked.connect(self.new_class)
        layout.addWidget(btn)

        new_subclass_btn = QPushButton('Dodaj podklasę')
        new_subclass_btn.clicked.connect(self.new_subclass)
        layout.addWidget(new_subclass_btn)

        main_layout.addLayout(layout)

        container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        container.setLayout(self.container_layout)

    
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def new_class(self):
        class_name, ok = QInputDialog.getText(self, 'Dodaj Klasę', 'Klasa:')
        if ok and class_name:
            if class_name in self.data['classes'].keys():
                QMessageBox.warning(self, 'Uwaga', 'Taka klasa już istnieje')
            else:
                self.data['classes'][class_name] = {'subjects': {'a':{}, 'extra': {}}, 'students': {'a': {}}}
                self.list.addItem(class_name)

    def new_subclass(self):
        class_name = self.list.currentText()
        if not class_name:
            return False
        class_dict = self.data['classes'][class_name]
        subclasses = class_dict['students'].keys()
        subclass_name = ascii_lowercase[len(subclasses)]
        class_dict['students'][subclass_name] = {}
        class_dict['subjects'][subclass_name] = {}
        self.load_class()

    def remove_subclass(self, subclass):
        def func():
            class_name = self.list.currentText()
            if not class_name:
                return False
            if len(self.data['classes'][class_name]['students'].keys()) == 1:
                QMessageBox.information(self, 'Uwaga', 'Nie możesz usunąć jedynej podklasy')
                return False
            if QMessageBox.question(self, 'Uwaga', f'Czy na pewno chcesz usunąć: {subclass.upper()}') != QMessageBox.StandardButton.Yes:
                return False
            self.data['classes'][class_name]['students'].pop(subclass)
            remaining_subclases = self.data['classes'][class_name]['students'].values()
            self.data['classes'][class_name]['students'] = dict(zip(list(ascii_lowercase), remaining_subclases))
            self.load_class() 
        return func

    def load_data(self, data):
        self.data = data
        self.list.clear()
        self.list.addItems(self.data['classes'].keys())
    
    def load_class(self):
        #clear widget
        for i in range(self.container_layout.count()):
            self.container_layout.itemAt(i).widget().deleteLater()

        frame = QWidget() 
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)
        self.container_layout.addWidget(frame)
        #classes data
        class_name = self.list.currentText()
        if not class_name:
            return False
        students_dict = self.data['classes'][class_name]['students'].items()
        for subclass, students in students_dict:
            scrollarea = QScrollArea()
            student_list_widget = QWidget()
            scrollarea.setWidget(student_list_widget)
            scrollarea.setMinimumHeight(200//len(students_dict))
            student_list = QGridLayout()
            student_list_widget.setLayout(student_list) 
            student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            scrollarea.setWidgetResizable(True)

            #subclass name
            frame_layout.addWidget(QLabel(subclass.upper()))
            #headers
            main_checkbox = QCheckBox()
            main_checkbox.toggled.connect(self.toggle_all_checkboxes)
            student_list.addWidget(main_checkbox, 0, 0)
            student_name_label = QLabel('Uczeń')
            student_name_label.setMinimumWidth(100)
            student_list.addWidget(student_name_label, 0, 1)
            student_list.addWidget(QLabel("Przedmioty podstawowe"), 0, 2)
            student_list.addWidget(QLabel("Przedmioty rozszerzone"), 0, 3)

            #load students
            for student in students.items():
                self.add_student_to_list(subclass, student, student_list)

            frame_layout.addWidget(scrollarea)

            bottom_button_group = QHBoxLayout()
            frame_layout.addLayout(bottom_button_group)
            new_name = QLineEdit()
            new_name.setPlaceholderText('Imię i nazwisko')
            new_name.setObjectName(f'new_name_{subclass}')
            new_name.returnPressed.connect(self.new_student(subclass, student_list))
            bottom_button_group.addWidget(new_name)
            add_student_btn = QPushButton("Dodaj ucznia")
            add_student_btn.clicked.connect(self.new_student(subclass, student_list))
            bottom_button_group.addWidget(add_student_btn)
            delete_student_button = QPushButton("Usuń ucznia")
            delete_student_button.clicked.connect(self.remove_students(subclass, student_list_widget))
            bottom_button_group.addWidget(delete_student_button)
            add_subject_to_student_btn = QPushButton("Dodaj przedmiot")
            add_subject_to_student_btn.clicked.connect(self.add_subject_to_student(subclass, student_list_widget))
            bottom_button_group.addWidget(add_subject_to_student_btn)
            remove_subclass_btn = QPushButton('Usuń podklasę')
            remove_subclass_btn.clicked.connect(self.remove_subclass(subclass))
            bottom_button_group.addWidget(remove_subclass_btn)


    def del_btn(self, subclass, student_name, type):
        def func():
            btn = self.sender()
            class_name = self.list.currentText()
            self.data['classes'][class_name]['students'][subclass][student_name][type].remove(btn.text())
            btn.deleteLater()
        return func
    
    def add_subject_to_student(self, subclass: str, student_list:QWidget):
        def func():
            checkboxes = [checkbox for checkbox in student_list.findChildren(QCheckBox)[1:] if checkbox.isChecked()]
            if not checkboxes:
                return False
            class_name = self.list.currentText()
            dialog = AddSubjectDialog(self, class_name, subclass, self.data)
            ok = dialog.exec()
            if not ok:
                return False
            type = dialog.type_list.currentData()
            subject_name = dialog.subject_list.currentText()
            for checkbox in checkboxes:
                index = student_list.layout().indexOf(checkbox)
                label:QLabel = student_list.layout().itemAt(index+1).widget()
                student_name = label.text()
                subject_list = self.data['classes'][class_name]['students'][subclass][student_name][type]
                if subject_name not in subject_list:
                    self.data['classes'][class_name]['students'][subclass][student_name][type].append(subject_name)
                    btn = QPushButton(subject_name)
                    slw_index = index + (2 if type == subclass else 3)
                    student_list.layout().itemAt(slw_index).insertWidget(0,btn)
                    btn.clicked.connect(self.del_btn(subclass, student_name, type=='extra'))
        return func

    def add_student_to_list(self, subclass, student, student_list: QGridLayout): 
        n = student_list.rowCount()
        student_name, subjects = student
        #checkbox
        checkbox = QCheckBox()
        checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        student_list.addWidget(checkbox,n, 0)
        #name
        name_label = QLabel(student_name)
        name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        student_list.addWidget(name_label, n, 1)
        #basic subjects
        basic_subject_list = QHBoxLayout()
        for subject in subjects[subclass]:
            btn = QPushButton(subject)
            basic_subject_list.addWidget(btn)
            btn.clicked.connect(self.del_btn(subclass, student_name, subclass))
        basic_subject_list.addStretch()
        student_list.addLayout(basic_subject_list, n, 2)

        extra_subject_list = QHBoxLayout()
        for subject in subjects['extra']:
            btn = QPushButton(subject)
            extra_subject_list.addWidget(btn)
            btn.clicked.connect(self.del_btn(subclass, student_name, 'extra'))
        extra_subject_list.addStretch()
        student_list.addLayout(extra_subject_list, n, 3)

    def new_student(self, subclass, student_list):
        def func():
        # name_box = self.sender().parent()
            new_name:QLineEdit = self.findChild(QLineEdit, f'new_name_{subclass}')
            # student_list:QWidget = curr_widget.findChild(QGridLayout)
            student_name = new_name.text()
            new_name.clear()
            students = self.data['classes'][self.list.currentText()]['students'][subclass]
            if student_name and student_name not in students.keys():        
                self.add_student_to_list(subclass, (student_name, {subclass: [], 'extra': []}), student_list)
                students[student_name] = {subclass: [], 'extra': []}
        return func

    def toggle_all_checkboxes(self):
        curr_widget:QWidget = self.sender().parent()
        checkboxes: list[QCheckBox] = curr_widget.findChildren(QCheckBox)
        new_state = checkboxes[0].isChecked()
        for chechbox in checkboxes:
            chechbox.setChecked(new_state)

    def remove_students(self, subclass, student_list):
        def func():
            checkboxes:list[QCheckBox] = student_list.findChildren(QCheckBox)
            to_remove = []
            student_list_layout = student_list.layout()
            for checkbox in checkboxes[1:]:
                if checkbox.isChecked():
                    index = student_list_layout.indexOf(checkbox)
                    label:QLabel = student_list_layout.itemAt(index+1).widget()
                    student_name = label.text()
                    to_remove.append((student_list_layout.indexOf(label), student_name))
            amount = len(to_remove)
            if amount == 0:
                return False
            message = f"Czy na pewno chcesz usunąć {amount} {'ucznia' if amount == 1 else 'uczniów'}?"
            if QMessageBox.question(self, 'Uwaga', message) != QMessageBox.StandardButton.Yes:
                return False

            for i, student_name in to_remove[::-1]:
                self.data['classes'][self.list.currentText()]['students'][subclass].pop(student_name)
                for n in range(i-1, i+2):
                    item = student_list_layout.itemAt(n)
                    if item.widget():
                        item.widget().deleteLater()
                    layout = item.layout()
                    if layout:
                        for j in range(layout.count()-1):
                            layout.itemAt(j).widget().deleteLater()
        return func
                    
                

