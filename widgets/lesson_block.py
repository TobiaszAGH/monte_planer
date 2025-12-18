from PyQt5.QtWidgets import QGraphicsRectItem, QWidget, QToolTip, QGraphicsScene, QMenu, QAction, QDialogButtonBox, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QTextOption
from PyQt5.QtCore import Qt, QPoint
from random import randint
from data import Data, Class, Subclass, Block, Lesson
from functions import snap_position, display_hour
from widgets.add_lesson_dialog import AddLessonToBlockDialog

# class Foo(QWidget):

class LessonBlock(QGraphicsRectItem):
    def __init__(self, x,y,w,h, parent: QGraphicsScene, db):
        self.parent= parent
        self.db: Data = db
        super().__init__(x,y,w,h)
        color = QColor(randint(0,256), randint(0,256), randint(0,256), 210)
        self.setBrush(QBrush(color))
        # self.setZValue(100000)
        self.moved = False
        self.block: Block
        self.text_item = QGraphicsTextItem()
        self.text_item.contextMenuEvent = self.contextMenuEvent
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)
        self.text_item.document().setDefaultTextOption(option)
        self.text_item.setTextWidth(w)
        self.parent.addItem(self.text_item)

    def mousePressEvent(self, event):
        self.moved = True
        if event.button() == Qt.MouseButton.LeftButton:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.start_x = self.x()
        # if event.button() == Qt.MouseButton.RightButton:
        #     self.parent.removeItem(self)
        #     self.db.delete_block(self.block)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        remove_action = menu.addAction('Usuń')
        add_lesson_action = menu.addAction('Dodaj lekcję')
        remove_action.triggered.connect(self.delete)
        add_lesson_action.triggered.connect(self.add_subject)
        action = menu.exec(event.globalPos())

    def delete(self):
        self.parent.removeItem(self)
        self.db.delete_block(self.block)

    def add_subject(self):
        my_class = self.block.parent()
        dialog = AddLessonToBlockDialog(self, my_class)
        ok = dialog.exec()
        if not ok:
            return False
        subject = dialog.subject_list.currentData()
        lesson = dialog.lesson_list.currentData()
        if subject and lesson:
            # update db
            old_block: Block = lesson.block
                
            self.db.add_lesson_to_block(lesson, self.block)
            if old_block:
                old_block_item: LessonBlock = [bl for bl in self.parent.items() if isinstance(bl, LessonBlock) and bl.block==old_block][0]
                old_block_item.draw_lessons()
            self.draw_lessons()

    def bring_back(self):
        if self.isSelected():
            z_values = [item.zValue()  for item in self.collidingItems() if isinstance(item, LessonBlock)]
            if z_values:
                z = min(z_values) - 1
                self.setZValue(z)
                self.text_item.setZValue(z+0.1)

    def bring_forward(self):
        z_values = [item.zValue()  for item in self.collidingItems() if isinstance(item, LessonBlock)]
        if z_values:
            z = max(z_values) + 1
            self.setZValue(z)
            self.text_item.setZValue(z+0.1)

    def set_selectable(self, on:bool):
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, on)

    def set_movable(self, on:bool, five_min_h, top_bar_h):
        self.five_min_h = five_min_h
        self.top_bar_h = top_bar_h
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, on)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        start = (self.mapToScene(self.boundingRect()).boundingRect().y() - self.top_bar_h) // self.five_min_h + 1 
        # start = self.start_x + self.y() / self.five_min_h
        self.db.update_block_start(self.block, start)


    def y_in_scene(self):
        return self.mapToScene(self.boundingRect()).boundingRect().y() 
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.isSelected():
            # snap to grid
            x = self.start_x
            y = snap_position(self.y(), self.five_min_h)
            self.setPos(x, y)

            # correct if out of bounds
            while self.y_in_scene() + 1< self.top_bar_h:
                self.moveBy(0, self.five_min_h)
            while self.y_in_scene() + self.block.length*self.five_min_h > self.parent.height():
                self.moveBy(0, -self.five_min_h)

            self.bring_forward()

            # show tooltip
            start = (self.y_in_scene() - self.top_bar_h) // self.five_min_h + 1
            duration = self.block.length
            times = [start, start+duration]
            msg = '-'.join([display_hour(t) for t in times])
            if self.block.length>=0:
                msg += f' ({int(self.block.length)*5})'
            QToolTip.showText(event.screenPos(), msg)

            # move text
            self.recenter_text()

    def draw_lessons(self):
        text = '\n'.join([l.subject.name for l in self.block.lessons])
        self.text_item.setPlainText(text)
        self.text_item.setZValue(self.zValue()+0.1)
        self.recenter_text()
       
        

    def recenter_text(self):
        if not self.text_item:
            return False
        self.text_item.setPos(self.rect().center().x() - self.text_item.boundingRect().width()/2,\
                            self.y_in_scene() + self.rect().height()/2 - self.text_item.boundingRect().height()/2)

