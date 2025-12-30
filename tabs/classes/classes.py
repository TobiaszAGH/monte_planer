from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, \
    QComboBox, QMessageBox, QVBoxLayout, QCheckBox, QGridLayout, QLabel, QSizePolicy, \
    QLineEdit, QScrollArea, QDialog, QDialogButtonBox
from PyQt5.QtGui import QColor

from PyQt5.QtCore import Qt
from data import Data, Class, Subclass, Student, Subject
from sqlalchemy.exc import IntegrityError
from .reorder_classes_dialog import ReorderClassesDialog
from .subject_btn import SubjectButton

class AddSubjectDialog(QDialog):
    def __init__(self, parent, subclass: Subclass):
        super().__init__(parent)
        self.db = parent.db
        self.subclass: Subclass = subclass
        

        self.setWindowTitle('Wybierz przedmiot')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.type_list = QComboBox()
        layout.addWidget(self.type_list)
        self.type_list.addItems(['Przedmiot podstawowy', 'Przedmiot wspólny'])
        self.type_list.setItemData(0, True)
        self.type_list.setItemData(1, False)
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
        basic = self.type_list.currentData()
        if basic:
            subjects = self.subclass.subjects
        else:
            subjects = self.subclass.my_class.subjects
        self.subject_list.clear()
        for subject in subjects:
            self.subject_list.addItem(subject.name, subject) 

class ClassesWidget(QWidget):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.db: Data = parent.db

        main_layout = QVBoxLayout()

        layout= QHBoxLayout()
        self.list = QComboBox(self)
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

        rename_btn = QPushButton('Zmień nazwę')
        rename_btn.clicked.connect(self.rename_class)
        layout.addWidget(rename_btn)

        reorder_btn = QPushButton('Zmień kolejność')
        reorder_btn.clicked.connect(self.reorder_classes)
        layout.addWidget(reorder_btn)

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
                self.list.setCurrentText(my_class.name)
            except IntegrityError:
                QMessageBox.warning(self, 'Uwaga', 'Taka klasa już istnieje')


    def new_subclass(self):
        curr_class = self.list.currentData()
        if not curr_class:
            return False
        subclass = self.db.create_subclass(curr_class)
        self.load_class()
        return subclass
    
    def rename_class(self):
        class_ = self.list.currentData()
        name, ok = QInputDialog.getText(self, 'Zmień nazwę klasy', 'Nowa nazwa:', text=class_.name)
        if ok and name:
            try:
                self.db.update_class_name(class_, name)
                index = self.list.currentIndex()
                self.list.setItemText(index, name)
            except IntegrityError:
                QMessageBox.warning(self, 'Uwaga', 'Taka klasa już istnieje')
    
    def reorder_classes(self):
        btn = QMessageBox.question(self, 'Uwaga', 'Jesteś pewien? To może spowodować usunięcie części własnych bloków.')
        if btn != QMessageBox.StandardButton.Yes:
            return
        dialog = ReorderClassesDialog(self)
        ok = dialog.exec()
        if not ok:
            return
        
        for i in range(dialog.class_list.count()):
            class_ = dialog.class_list.item(i).data(Qt.UserRole)
            self.db.update_class_order(class_, i)

        self.db.delete_unplaceable_custom_blocks()
        
        self.load_data(self.db)

    def remove_subclass(self, subclass):
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

    def load_data(self, db):
        opened_class = self.list.currentText()
        self.db = db
        self.list.clear()
        for cl in self.db.all_classes():    
            self.list.addItem(cl.name, cl)
        try:
            self.list.setCurrentText(opened_class)
        except:
            pass
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
            student_list.addWidget(QLabel("Przedmioty wspólne"), 0, 3)

            #load students
            student: Student
            for student in sorted(subclass.students, key=lambda s: s.name):
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
        
            pass

    def add_subject_to_student(self, subclass: str, student_list:QWidget):
        def func():
            checkboxes = [checkbox for checkbox in student_list.findChildren(QCheckBox) if checkbox.isChecked()]
            if not checkboxes:
                return False
            dialog = AddSubjectDialog(self, subclass)
            ok = dialog.exec()
            if not ok:
                return False
            subject = dialog.subject_list.currentData()
            for checkbox in checkboxes:
                if hasattr(checkbox, 'student'):
                    if subject in checkbox.student.subjects:
                        continue
                    self.db.add_subject_to_student(subject, checkbox.student)
                    btn = SubjectButton(self, checkbox.student, subject)
                    index = student_list.layout().indexOf(checkbox) + 3 - subject.basic
                    layout = student_list.layout().itemAt(index).layout()
                    layout.insertWidget(layout.count()-1, btn)

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
        student_list.addLayout(basic_subject_list, n, 2)
        extra_subject_list = QHBoxLayout()
        student_list.addLayout(extra_subject_list, n, 3)
        subject: Subject
        for subject in student.subjects:
            btn = SubjectButton(self, student, subject)
            if subject.basic == True:
                basic_subject_list.addWidget(btn)
            else:
                extra_subject_list.addWidget(btn)
        basic_subject_list.addStretch()
        extra_subject_list.addStretch()

    def new_student(self, subclass, student_list):
        def func():
            new_name_box = self.findChild(QLineEdit, f'new_name_{subclass.name}')
            new_name = new_name_box.text()
            if not new_name:
                return
            class_name = self.db.student_exists(new_name)
            if class_name:
                QMessageBox.warning(self, 'Uwaga', f'Taki uczeń już istnieje! ({class_name})')
                return
            student = self.db.create_student(new_name, subclass)

            self.add_student_to_list(student, student_list)
            new_name_box.clear()
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
        self.load_data(self.db)
                    
                

