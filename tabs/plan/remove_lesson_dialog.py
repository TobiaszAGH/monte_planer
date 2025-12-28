from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox


class RemoveLessonFromBlockDialog(QDialog):
    def __init__(self, lessons):
        super().__init__()

        self.setWindowTitle('Wybierz przedmiot')
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list = QComboBox()
        layout.addWidget(self.list)

        represented_subclasses = list(set([lesson.subject.parent().name for lesson in lessons]))
        show_subclass_name = len(represented_subclasses)>1


        for lesson in lessons:
            self.list.addItem(lesson.subject.get_name(short=False, show_subclass_name=show_subclass_name), lesson) 

        buttonBox = QDialogButtonBox()
        layout.addWidget(buttonBox)

        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)



