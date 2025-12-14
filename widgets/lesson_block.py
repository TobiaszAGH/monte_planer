from PyQt5.QtWidgets import QGraphicsRectItem, QWidget
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt, QPoint
from random import randint
from data import Data
from functions import snap_position

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
        if event.button() == Qt.MouseButton.LeftButton:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.start_x = self.x()
        if event.button() == Qt.MouseButton.RightButton:
            self.parent.removeItem(self)
            self.db.delete_block(self.block)
        super().mousePressEvent(event)

    def bring_back(self):

        if self.isSelected():
            z = min([item.zValue() for item in self.collidingItems()]) - 1
            self.setZValue(z)

    def set_movable(self, on:bool, five_min_h, top_bar_h):
        self.five_min_h = five_min_h
        self.top_bar_h = top_bar_h
        if on:
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        else:
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, False)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        start = self.start_x + self.y() / self.five_min_h
        self.db.update_block_start(self.block, start)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.isSelected():
            x = self.start_x
            y = snap_position(self.y(), self.five_min_h)
            self.setPos(x, y)

