from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, \
    QComboBox, QMessageBox, QVBoxLayout, QCheckBox, QGridLayout, QLabel, QStackedLayout, QSizePolicy, \
    QLineEdit, QScrollArea, QSpacerItem, QDialog, QDialogButtonBox

from PyQt5.QtCore import Qt
from data import Data, Class, Subclass, Student, Subject
from sqlalchemy.exc import IntegrityError

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
        self.db: Data = parent.db

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

        layout.addStretch()
        
        delete_class_btn = QPushButton('Usuń klasę')
        delete_class_btn.clicked.connect(self.delete_class)
        layout.addWidget(delete_class_btn)

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
            try:
                my_class = self.db.create_class(class_name)
                self.list.addItem(my_class.name, my_class)
            except IntegrityError:
                QMessageBox.warning(self, 'Uwaga', 'Taka klasa już istnieje')


    def new_subclass(self):
        curr_class = self.list.currentData()
        if not curr_class:
            return False
        subclass = self.db.create_subclass(curr_class)
        self.load_class()
        return subclass

    def remove_subclass(self, subclass):
        # foo = subclass
        def func():
            my_class: Class = self.list.currentData()
            if not my_class:
                return False
            if len(my_class.subclasses) == 1:
                QMessageBox.information(self, 'Uwaga', 'Nie możesz usunąć jedynej podklasy')
                return False
            if QMessageBox.question(self, 'Uwaga', f'Czy na pewno chcesz usunąć: {subclass.name.upper()}') != QMessageBox.StandardButton.Yes:
                return False
            
            self.db.delete_subclass(subclass)
            
            self.load_class() 
        return func

    def load_data(self, data):
        self.data = data
        self.list.clear()
        for cl in self.db.all_classes():    
            self.list.addItem(cl.name, cl)
        # self.list.addItems(self.data['classes'].keys())
    
    def load_class(self):
        #clear widget
        for i in range(self.container_layout.count()):
            self.container_layout.itemAt(i).widget().deleteLater()

        frame = QWidget() 
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)
        self.container_layout.addWidget(frame)
        #classes data
        my_class: Class = self.list.currentData()
        if not my_class:
            return False
        subclass: Subclass
        for subclass in my_class.subclasses:
            scrollarea = QScrollArea()
            student_list_widget = QWidget()
            scrollarea.setWidget(student_list_widget)
            scrollarea.setMinimumHeight(200//len(my_class.subclasses))
            student_list = QGridLayout()
            student_list_widget.setLayout(student_list) 
            student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            scrollarea.setWidgetResizable(True)

            #subclass name
            frame_layout.addWidget(QLabel(subclass.name.upper()))
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
            student: Student
            for student in subclass.students:
                self.add_student_to_list(student, student_list)

            frame_layout.addWidget(scrollarea)

            bottom_button_group = QHBoxLayout()
            frame_layout.addLayout(bottom_button_group)
            new_name = QLineEdit()
            new_name.setPlaceholderText('Imię i nazwisko')
            new_name.setObjectName(f'new_name_{subclass.name}')
            new_name.returnPressed.connect(self.new_student(subclass, student_list))
            bottom_button_group.addWidget(new_name)
            add_student_btn = QPushButton("Dodaj ucznia")
            add_student_btn.clicked.connect(self.new_student(subclass, student_list))
            bottom_button_group.addWidget(add_student_btn)
            delete_student_button = QPushButton("Usuń ucznia")
            delete_student_button.clicked.connect(self.delete_students(student_list_widget))
            bottom_button_group.addWidget(delete_student_button)
            add_subject_to_student_btn = QPushButton("Dodaj przedmiot")
            add_subject_to_student_btn.clicked.connect(self.add_subject_to_student(subclass, student_list_widget))
            bottom_button_group.addWidget(add_subject_to_student_btn)
            remove_subclass_btn = QPushButton('Usuń podklasę')
            remove_subclass_btn.clicked.connect(self.remove_subclass(subclass))
            bottom_button_group.addWidget(remove_subclass_btn)


    def del_btn(self, student, subject):
        def func():
            self.db.remove_subject_from_student(subject, student)
            self.sender().deleteLater()
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

    def add_student_to_list(self, student, student_list: QGridLayout): 
        n = student_list.rowCount()
        #checkbox
        checkbox = QCheckBox()
        checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        checkbox.student = student
        student_list.addWidget(checkbox,n, 0)
        #name
        name_label = QLabel(student.name)
        name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        student_list.addWidget(name_label, n, 1)
        #basic subjects
        basic_subject_list = QHBoxLayout()
        extra_subject_list = QHBoxLayout()
        subject: Subject
        for subject in student.subjects:
            btn = QPushButton(subject.name)
            basic_subject_list.addWidget(btn)
            btn.clicked.connect(self.del_btn(student, subject))
            if subject.basic:
                basic_subject_list.addWidget(btn)
            else:
                extra_subject_list.addWidget(btn)
        basic_subject_list.addStretch()
        extra_subject_list.addStretch()
        student_list.addLayout(basic_subject_list, n, 2)
        student_list.addLayout(extra_subject_list, n, 3)

    def new_student(self, subclass, student_list):
        def func():
            new_name:QLineEdit = self.findChild(QLineEdit, f'new_name_{subclass.name}')
            student = self.db.create_student(new_name.text(), subclass)
            self.add_student_to_list(student, student_list)
            new_name.clear()
        return func

    def toggle_all_checkboxes(self):
        curr_widget:QWidget = self.sender().parent()
        checkboxes: list[QCheckBox] = curr_widget.findChildren(QCheckBox)
        new_state = checkboxes[0].isChecked()
        for chechbox in checkboxes:
            chechbox.setChecked(new_state)

    def delete_students(self, student_list):
        def func():
            checkboxes:list[QCheckBox] = student_list.findChildren(QCheckBox)[1:]
            to_remove = [ch.student for ch in checkboxes if ch.isChecked()]
            amount = len(to_remove)
            if amount == 0:
                return False

            message = f"Czy na pewno chcesz usunąć {amount} {'ucznia' if amount == 1 else 'uczniów'}?"
            if QMessageBox.question(self, 'Uwaga', message) != QMessageBox.StandardButton.Yes:
                return False

            for student in to_remove:
                self.db.delete_student(student)

            self.load_class()

        return func

    def delete_class(self):
        my_class: Class = self.list.currentData()
        if QMessageBox.question(self, 'Uwaga', f'Czy na pewno chcesz usunąć klasę: {my_class.name}') == QMessageBox.StandardButton.Yes:
            self.db.delete_class(my_class)
        self.load_data(self.data)
                    
                

