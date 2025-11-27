from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QComboBox, QTableWidget, QGridLayout,\
      QLabel, QInputDialog, QMessageBox, QPushButton, QHBoxLayout, QDialogButtonBox
      
from PyQt5 import QtCore

cell_style = 'border: 1px solid black;'

class AvailabilityCell(QWidget):
    def __init__(self, row, col):
        super().__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(cell_style)
        self.setMouseTracking(True)
        self.mouseMoveEvent= self.moved
        self.row = row
        self.col = col
        self.available = False
        self.mousePressEvent=self.clicked

    def set_highlight(self, highlight):
        self.setStyleSheet(cell_style + f'background: {"pink" if highlight else "white"}')
    
    def show_true_color(self):
        self.setStyleSheet(cell_style + f'background: {"red" if self.available else "white"}')


    def clicked(self, event):
        parent = self.parent()
        parent.change_availability = not parent.change_availability
        if parent.change_availability:
            parent.availability_mode = not self.available
            parent.start_highlight(self.row, self.col)
        else:
            parent.set_availability(self.row, self.col)

    def moved(self, event):
        if self.parent().change_availability:
            self.parent().highlight_to(self.row, self.col)
        
class AvFrame(QWidget):
    def __init__(self):
        super().__init__()
        self.change_availability = False
        self.availability = QGridLayout()
        self.availability.setSpacing(0)
        headers = 'Godzina: Poniedziałek: Wtorek: Środa: Czwartek: Piątek:'.split()
        for col, head in enumerate(headers):
            cell = QLabel(head)
            cell.setStyleSheet(cell_style)
            self.availability.addWidget(cell, 0, col)

        for n in range(8,16):
            cell_1 = QLabel(f'{n}:00-{n}:30')
            cell_2 = QLabel(f'{n}:30-{n+1}:00')
            cell_1.setStyleSheet(cell_style)
            cell_2.setStyleSheet(cell_style)
            row = (n-8)*2+1
            self.availability.addWidget(cell_1, row, 0)
            self.availability.addWidget(cell_2, row+1, 0)

        for col in range(1,6):
            for row in range(1,17):
                cell = AvailabilityCell(row, col)
                self.availability.addWidget(cell, row, col)

        self.setLayout(self.availability)

    
    def start_highlight(self, row, col):
        self.s_row = row
        self.s_col = col

    def highlight_to(self, e_row, e_col):
        s_row = min(self.s_row, e_row)
        e_row = max(self.s_row, e_row)
        s_col = min(self.s_col, e_col)
        e_col = max(self.s_col, e_col)
        for row in range(1,17):
            for col in range(1,6):
                if s_row <= row and row <= e_row and \
                   s_col <= col and col <= e_col:
                    self.availability.itemAtPosition(row, col).widget().set_highlight(self.availability_mode)
                else:
                    self.availability.itemAtPosition(row, col).widget().show_true_color()

    def set_availability(self, e_row, e_col):
        s_row = min(self.s_row, e_row)
        e_row = max(self.s_row, e_row)
        s_col = min(self.s_col, e_col)
        e_col = max(self.s_col, e_col)
        for row in range(1,17):
            for col in range(1,6):
                if s_row <= row and row <= e_row and \
                    s_col <= col and col <= e_col:
                    self.availability.itemAtPosition(row, col).widget().available = self.availability_mode
                self.availability.itemAtPosition(row, col).widget().show_true_color()
        self.parent().parent().save_av()

class TeachersWidget(QWidget):
    def __init__(self,parent, data):
        super().__init__(parent=parent)
        self.data = data

        layout= QVBoxLayout()
        top_row = QHBoxLayout()
        self.list = QComboBox(self)
        self.list.currentTextChanged.connect(self.load_teacher_av)
        self.list.addItems(data['teachers'].keys())
        top_row.addWidget(self.list)

        self.new_teacher_btn = QPushButton('Dodaj Nauczyciela')
        self.new_teacher_btn.clicked.connect(self.new_teacher)
        top_row.addWidget(self.new_teacher_btn)

        layout.addLayout(top_row)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        self.frame = AvFrame()
        container_layout.addWidget(self.frame)

        layout.addWidget(container)
        if not self.list.currentText():
            self.frame.hide()

        # del_teacher_btn = QAbstractButton('Usuń Nauczyciela')
        self.button_row = QDialogButtonBox()
        del_teacher_btn = self.button_row.addButton('Usuń nauczyciela', QDialogButtonBox.ButtonRole.ActionRole)
        del_teacher_btn.clicked.connect(self.del_teacher)
        layout.addWidget(self.button_row)
        self.setLayout(layout)

    def new_teacher(self):
        teacher_name, ok = QInputDialog.getText(self, 'Dodaj Nauczyciela', 'Nauczyciel:')
        if ok and teacher_name:
            if teacher_name in self.data['teachers'].keys():
                QMessageBox.warning(self, 'Uwaga', 'Taki nauczyciel już istnieje')
            else:
                self.data['teachers'][teacher_name] = [[0] * 16] * 5
                self.list.addItem(teacher_name)
                self.list.setCurrentText(teacher_name)

    def del_teacher(self):
        name = self.list.currentText()
        self.list.removeItem(self.list.currentIndex())
        self.data["teachers"].pop(name)
        for cl in self.data['classes'].values():
            for subject in cl['subjects'].values():
                if subject['teacher'] == name:
                    subject['teacher'] = ''
        self.load_teacher_av()

    def load_teacher_av(self):
        teacher = self.list.currentText()
        if not teacher:
            self.frame.hide()
            return False
        self.frame.show()
        av = self.data['teachers'][teacher]
        for row in range(1,17):
            for col in range(1,6):
                cell = self.frame.availability.itemAtPosition(row, col).widget()
                cell.available = av[col-1][row-1]
                cell.show_true_color()

    def save_av(self):
        teacher = self.list.currentText()
        if not teacher:
            return False
        av = [
            [
                int(self.frame.availability.itemAtPosition(row, col).widget().available) for row in range(1,17)
            ] for col in range(1,6)
        ]
        self.data['teachers'][teacher] = av


    def load_data(self, data):
        self.data = data
        self.list.clear()
        self.list.addItems(self.data['teachers'].keys())
        if self.list.currentText():
            self.frame.show()
