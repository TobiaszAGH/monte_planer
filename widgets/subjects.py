from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout

class SubjectsWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)

        layout= QVBoxLayout()
        self.list = QListWidget(self)
        self.list.addItems(cl['name'] for cl in data['subjects'])
        layout.addChildWidget(self.list)

        self.setLayout(layout)

        
