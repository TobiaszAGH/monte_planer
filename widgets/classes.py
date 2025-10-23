from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, \
    QComboBox, QMessageBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox

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
        self.btn.clicked.connect(self.open_input_dialog)
        layout.addWidget(self.btn)

        main_layout.addLayout(layout)

        self.student_list = QVBoxLayout()
        main_layout.addLayout(self.student_list)


        self.setLayout(main_layout)

    def open_input_dialog(self):
        class_name, ok = QInputDialog.getText(self, 'Dodaj Klasę', 'Klasa:')
        if ok and class_name:
            if class_name in self.data['classes'].keys():
                QMessageBox.warning(self, 'Uwaga', 'Taka klasa już istnieje')
            else:
                self.data['classes'][class_name] = []
                self.list.addItem(class_name)

    def load_data(self, data):
        self.data = data
        self.list.clear()
        self.list.addItems(self.data['classes'].keys())
        
    def populate_student_list(self):
        selected_class = self.list.currentText()
        if selected_class:
            students = self.data['classes'][selected_class]
            print(f'selected class: {selected_class}, students: {students}')
            # self.student_list.setRowCount(len(students))
            # self.student_list.setColumnCount(1)
            for item in self.student_list.children():
                print(item.text())
                item.deleteLater()
            
            for n, student in enumerate(students):
                print(student['name'])
                self.student_list.addWidget(QCheckBox(student['name']))
