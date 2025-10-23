from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, \
    QComboBox, QMessageBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox, QAbstractItemView, QButtonGroup, \
    QGridLayout, QLabel, QStackedLayout, QTabWidget, QSizePolicy, QToolButton, QLayout

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
        self.btn.clicked.connect(self.open_input_dialog)
        layout.addWidget(self.btn)

        main_layout.addLayout(layout)

        # self.student_list = QTableWidget()
        # self.student_list.setColumnCount(2)
        # self.student_list.setHorizontalHeaderLabels(["Uczeń","Rozszerzenia"])
        # self.student_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        student_list_area = QWidget()
        self.student_list_area_layout = QStackedLayout()
        student_list_area.setLayout(self.student_list_area_layout)
        
        main_layout.addWidget(student_list_area)


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
        
        for i, students in enumerate(data['classes'].values()):
            
            student_list_widget = QWidget()
            student_list = QGridLayout()
            student_list.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            # student_list.setColumnStretch(2, 8)

            student_list.addWidget(QCheckBox(), 0, 0)
            student_list.addWidget(QLabel("Uczeń"), 0, 1)
            student_list.addWidget(QLabel("Rozszerzenia"), 0, 2)
            for n, [student_name, subjects] in enumerate(students.items()):
                    n = n+1
                    checkbox = QCheckBox()
                    checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
                    student_list.addWidget(checkbox,n, 0)
                    name_label = QLabel(student_name)
                    name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
                    student_list.addWidget(name_label, n, 1)

                    subject_list = QHBoxLayout()
                    for subject in subjects:
                        # print(f'student {student["name"]}: {subject}')
                        btn = QPushButton(subject)
                        btn.setObjectName(student_name)
                        subject_list.addWidget(btn)
                        btn.clicked.connect(self.del_btn)

                    
                    student_list.addLayout(subject_list, n, 2)

            student_list_widget.setLayout(student_list)
            self.student_list_area_layout.insertWidget(i, student_list_widget)
        self.student_list_area_layout.setCurrentIndex(0)

        
    def populate_student_list(self):
        selected_class = self.list.currentIndex()
        self.student_list_area_layout.setCurrentIndex(selected_class)

    def del_btn(self):
        btn = self.sender()
        student_name = btn.objectName()
        class_name = self.list.currentText()
        self.data['classes'][class_name][student_name].remove(btn.text())
        btn.deleteLater()

        
