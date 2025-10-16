from PyQt5.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QPushButton, QComboBox, QMessageBox

class ClassesWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)
        self.data = data

        layout= QHBoxLayout()
        self.list = QComboBox(self)
        self.list.addItems(data['classes'].keys())
        layout.addWidget(self.list)

        self.btn = QPushButton('Dodaj klasę')
        self.btn.clicked.connect(self.open_input_dialog)
        layout.addWidget(self.btn)

        self.setLayout(layout)

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
        
