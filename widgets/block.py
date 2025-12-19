from __future__ import annotations
from PyQt5.QtWidgets import QGraphicsRectItem, QToolTip, QGraphicsScene
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from data import Data, Class, LessonBlockDB
from functions import snap_position, display_hour, contrast_ratio
from widgets.block_text import BlockText


class BasicBlock(QGraphicsRectItem):
    def __init__(self, x,y,w,h, parent: QGraphicsScene, db, visible_classes):
        self.parent= parent
        self.db: Data = db
        super().__init__(x,y,w,h)
        color = QColor('#c0c0c0')
        color.setAlpha(210)
        self.setBrush(QBrush(color))
        self.moved = False
        self.block: LessonBlockDB
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

    def bring_back(self):
        if self.isSelected():
            z_values = [item.zValue()  for item in self.collidingItems() if isinstance(item, LessonBlockDB)]
            if z_values:
                z = min(z_values) - 1
                self.setZValue(z)
                self.text_item.setZValue(z+0.1)

    def bring_forward(self):
        z_values = [item.zValue()  for item in self.collidingItems() if isinstance(item, LessonBlockDB)]
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
        lessons = [l for l in self.block.lessons 
                   if isinstance(l.subject.parent(), Class) 
                   or l.subject.parent() in self.visible_classes
                   or len(l.subject.parent().get_class().subclasses) == 1]

        # pick background color
        color = lessons[0].subject.color if len(lessons) == 1 else '#c0c0c0'
        color = QColor(color)
        color.setAlpha(210)
        self.setBrush(QBrush(color))

        # pick contrasting text color
        if contrast_ratio(color, QColor('black')) < 4.5:
            self.text_item.setDefaultTextColor(QColor('#ffffff'))

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
        return [
            (l.subject.full_name(), l.subject.short_full_name())
            if l.subject.my_class or (self.block.class_id and self.other_subclasses_visible())
            else (l.subject.name, l.subject.short_name)
            for l in lessons
        ]