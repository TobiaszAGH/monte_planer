from PyQt5.QtWidgets import QGraphicsRectItem, QWidget
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from random import randint
from data import Data

# class Foo(QWidget):

class LessonBlock(QGraphicsRectItem):
    def __init__(self, x,y,w,h, parent, db):
        self.parent= parent
        self.db: Data = db
        super().__init__(x,y,w,h)
        color = QColor(randint(0,256), randint(0,256), randint(0,256), 128)
        self.setBrush(QBrush(color))
        self.setZValue(10)

    def mousePressEvent(self, event):
        # super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.parent.removeItem(self)
            self.db.delete_block(self.block)


