from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox


class RemoveLessonFromBlockDialog(QDialog):
    def __init__(self, lessons):
        super().__init__()

        self.setWindowTitle('Wybierz przedmiot')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list = QComboBox()
        layout.addWidget(self.list)


        for lesson in lessons:
            self.list.addItem(lesson[0][0], lesson[1]) 

        buttonBox = QDialogButtonBox()
        layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



