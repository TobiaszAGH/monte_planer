from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QListWidget, QAbstractItemView, QListWidgetItem
from PyQt5.QtCore import Qt


class ReorderClassesDialog(QDialog):
    def __init__(self, parent = ...):
        super().__init__(parent)
        self.db = parent.db

        self.setWindowTitle('Zmień kolejność')
        self.setLayout(QVBoxLayout())

        self.class_list = QListWidget()
        self.layout().addWidget(self.class_list)
        self.class_list.setDragEnabled(True)
        self.class_list.setAcceptDrops(True)
        self.class_list.setDropIndicatorShown(True)
        self.class_list.setDragDropMode(QAbstractItemView.InternalMove)
        for class_ in self.db.all_classes():
            item = QListWidgetItem(class_.name)
            item.setData(Qt.UserRole, class_)
            self.class_list.addItem(item)

        self.buttons = QDialogButtonBox()
        self.layout().addWidget(self.buttons)

        
        self.buttons.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)