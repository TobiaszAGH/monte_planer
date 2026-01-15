from PyQt5.QtWidgets import QProgressBar, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class ProgressDialog(QWidget):
    def __init__(self, title, total):
        super().__init__()
        self.setMinimumWidth(300)
        self.curr = 0
        self.total = total
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel()
        layout.addWidget(self.label)
        self.bar = QProgressBar()
        layout.addWidget(self.bar)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def set_label(self, label):
        self.label.setText(label)

    def next(self):
        self.curr += 1
        self.bar.setValue(int(self.curr/self.total*100))