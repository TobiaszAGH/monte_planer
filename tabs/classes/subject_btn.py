from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from data import Student, Subject, Data
from functions import contrast_ratio

class SubjectButton(QPushButton):
    def __init__(self, parent, student: Student, subject: Subject):
        super().__init__()
        self.db: Data = parent.db
        self.setText(subject.name)
        self.student = student
        self.subject = subject
        bg_color = QColor(subject.color)
        text_color  = '#000000' if contrast_ratio(bg_color, QColor('black')) > 4.5 else '#ffffff'
        self.setStyleSheet(f'color: {text_color}; background-color: {bg_color.name()}')
        
    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.setCheckable(True)
        self.setChecked(True)
    
    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        # print(e.button)
        if e.button() == Qt.RightButton:
            self.db.remove_subject_from_student(self.subject, self.student)
            self.deleteLater()