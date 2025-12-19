from __future__ import annotations
from PyQt5.QtWidgets import QGraphicsRectItem, QWidget, QToolTip, QGraphicsScene, QMenu, QAction, QDialogButtonBox, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QTextOption, QFontMetrics
from PyQt5.QtCore import Qt, QPoint
from random import randint
from data import Data, Class, Subclass, Block, Lesson, Subject
from functions import snap_position, display_hour, contrast_ratio
from widgets.add_lesson_dialog import AddLessonToBlockDialog
from widgets.remove_lesson_dialog import RemoveLessonFromBlockDialog
from typing import List


class BlockText(QGraphicsTextItem):
    def __init__(self, parent: LessonBlock, w):
        super().__init__()
        self.contextMenuEvent = parent.contextMenuEvent
        self.bring_back = parent.bring_back
        self.bring_forward = parent.bring_forward
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)
        self.document().setDefaultTextOption(option)
        self.setTextWidth(w)
        self.w = w
        self.row_num = 0

    def shrink(self):
        if not self.row_num:
            return 
        font = self.font()
        size = font.pointSize()
        if self.text_too_big():
            self.shorten_names()
        while self.text_too_big() and size >=4:
            size -= 0.2
            font.setPointSizeF(size)
            self.setFont(font)
            # print(self.font().pointSize())

    def shorten_names(self) -> None:
        self.setHtml('<br>'.join([l[1] for l in self.lessons]))

    def text_too_big(self) -> bool:
        wrapping = self.document().begin().layout().lineCount() > self.row_num
        overflowing = self.boundingRect().width() > self.w
        return wrapping or overflowing
    
    def set_lessons(self, lessons):
        self.lessons = lessons
        self.row_num = len(lessons)
        self.setHtml('<br>'.join([l[0] for l in lessons]))


            


class LessonBlock(QGraphicsRectItem):
    def __init__(self, x,y,w,h, parent: QGraphicsScene, db, visible_classes):
        self.parent= parent
        self.db: Data = db
        super().__init__(x,y,w,h)
        color = QColor('#c0c0c0')
        color.setAlpha(210)
        self.setBrush(QBrush(color))
        # self.setZValue(100000)
        self.moved = False
        self.block: Block
        self.text_item = BlockText(self, w)
        self.parent.addItem(self.text_item)
        self.visible_classes = visible_classes

    def mousePressEvent(self, event):
        self.moved = True
        if event.button() == Qt.MouseButton.LeftButton:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.start_x = self.x()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        remove_action = menu.addAction('Usuń')
        remove_action.triggered.connect(self.delete)
        add_lesson_action = menu.addAction('Dodaj lekcję')
        add_lesson_action.triggered.connect(self.add_subject)
        remove_lesson_action = menu.addAction('Usuń lekcję')
        remove_lesson_action.triggered.connect(self.remove_lesson)
        action = menu.exec(event.globalPos())

    def delete(self):
        self.parent.removeItem(self)
        self.parent.removeItem(self.text_item)
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
            old_block: Block = lesson.block
                
            # update db
            self.db.add_lesson_to_block(lesson, self.block)
        
            # update visuals
            if old_block:
                old_block_item: LessonBlock = [bl for bl in self.parent.items() if isinstance(bl, LessonBlock) and bl.block==old_block][0]
                old_block_item.draw_lessons()
            self.draw_lessons()

    def remove_lesson(self):
        if not self.block.lessons:
            return False
        dialog = RemoveLessonFromBlockDialog(self.lessons)
        ok = dialog.exec()
        if not ok:
            return False
        lesson = dialog.list.currentData()
        self.db.remove_lesson_from_block(lesson)
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
        # pick which lessons to draw
        lessons = [l for l in self.block.lessons if isinstance(l.subject.parent(), Class) or l.subject.parent() in self.visible_classes]

        # pick background color
        color = lessons[0].subject.color if len(lessons) == 1 else '#c0c0c0'
        color = QColor(color)
        color.setAlpha(210)
        self.setBrush(QBrush(color))

        # pick contrasting text color
        if contrast_ratio(color, QColor('black')) < 4.5:
            self.text_item.setDefaultTextColor(QColor('#d0d0d0'))

        # get correct suffixes
        lesson_names = self.lesson_names(lessons)
        self.lessons = zip(lesson_names, lessons)

        # write on screen
        self.text_item.set_lessons(lesson_names)
        self.text_item.setZValue(self.zValue()+0.1)

        self.recenter_text()
       
        

    def recenter_text(self):
        if not self.text_item:
            return False
        self.text_item.shrink()
        self.text_item.setPos(self.rect().center().x() - self.text_item.boundingRect().width()/2,\
                            self.y_in_scene() + self.rect().height()/2 - self.text_item.boundingRect().height()/2)
        
    def other_subclasses_visible(self):
        my_class = self.block.parent().get_class()
        n = sum([1 for cl in self.visible_classes if cl.get_class() == my_class])
        return n > 1
    
    def lesson_names(self, lessons):
        list = [
            (l.subject.full_name(), l.subject.short_full_name())
            if l.subject.my_class or (self.block.class_id and self.other_subclasses_visible())
            else (l.subject.name, l.subject.short_name)
            for l in lessons
        ]
        return list