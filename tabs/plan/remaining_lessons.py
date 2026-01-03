from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QPushButton, QSizePolicy, QTreeWidgetItem
from PyQt5.QtCore import QSize, Qt, QPoint
from PyQt5.QtGui import QCursor
from data import Data

class RemainingLessonsWindow(QWidget):
    def __init__(self, db: Data):
        super().__init__()
        self.db = db
        self.setMinimumSize(QSize(300, 400))
        self.setWindowTitle('Pozostałe lekcje')
        self.setLayout(QVBoxLayout())
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel('Przedmioty')
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # scroll_area = QScrollArea(self)
        # scroll_area.setWidget(self.tree)
        # self.layout().addWidget(scroll_area)
        self.layout().addWidget(self.tree)
        refresh_btn = QPushButton('Odśwież')
        refresh_btn.clicked.connect(self.load)
        self.layout().addWidget(refresh_btn)
        
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.move(QCursor.pos() + QPoint(10,10))

    def load(self):
        self.tree.clear()
        for class_ in self.db.all_classes():
            class_item = QTreeWidgetItem([class_.name])

            # wpólne
            extra = QTreeWidgetItem(class_item, ['Wspólne'])
            self.add_subjects_to_item(extra, class_.subjects)
            if not extra.childCount():
                class_item.removeChild(extra)

            # podstawowe
            for subclass in class_.subclasses:
                subclass_item = QTreeWidgetItem(class_item, [subclass.name.upper()])
                self.add_subjects_to_item(subclass_item, subclass.subjects)
                if not subclass_item.childCount():
                    class_item.removeChild(subclass_item)
            
            if class_item.childCount():
                self.tree.addTopLevelItem(class_item)
        self.tree.expandAll()

    def add_subjects_to_item(self, item: QTreeWidgetItem, subjects):
        for subject in subjects:
                subject_item = QTreeWidgetItem(item, [subject.get_name(0,0,0)])
                for lesson in subject.lessons:
                    if lesson.block is None:
                        QTreeWidgetItem(subject_item, [str(lesson.length)])
                if not subject_item.childCount():
                    item.removeChild(subject_item)
            

        
