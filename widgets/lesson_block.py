from PyQt5.QtWidgets import QGraphicsRectItem, QWidget
from PyQt5.QtGui import QBrush, QColor
from random import randint

# class Foo(QWidget):

class LessonBlock(QGraphicsRectItem):
    def __init__(self, x,y,w,h):
        super().__init__(x,y,w,h)
        color = QColor(randint(0,256), randint(0,256), randint(0,256), 128)
        self.setBrush(QBrush(color))

