from PyQt5.QtWidgets import QPushButton

class ModeBtn(QPushButton):
    def __init__(self, label, func, parent):
        super().__init__(label, parent)
        self.func = func
        self.setCheckable(True)
        self.setAutoExclusive(True)

    def mousePressEvent(self, event):
        self.func(not self.isChecked())
        if self.isChecked():
            self.uncheck()
        else: 
            super().mousePressEvent(event)

    def uncheck(self):
        self.setAutoExclusive(False)
        self.setChecked(False)
        self.setAutoExclusive(True)