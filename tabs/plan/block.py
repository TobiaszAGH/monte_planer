from __future__ import annotations
from PyQt5.QtWidgets import QGraphicsRectItem, QToolTip, QGraphicsScene, QMenu
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from data import Data, Class, LessonBlockDB
from functions import snap_position, display_hour, contrast_ratio
from .block_text import BlockText
from db_config import settings


class BasicBlock(QGraphicsRectItem):
    
    def contextMenuEvent(self, event):
        self.menu = QMenu()
        self.remove_action = self.menu.addAction('Usuń')
        self.remove_action.triggered.connect(self.delete)

    def __init__(self, x,y,w,h, parent: QGraphicsScene, db, visible_classes):
        self.parent= parent
        self.db: Data = db
        super().__init__(x,y,w,h)
        self.five_min_h = h
        # color = QColor('#c0c0c0')
        # color.setAlpha(210)
        # self.setBrush(QBrush(color))
        self.moved = False
        self.block: LessonBlockDB
        self.text_item0 = BlockText(self, w, h)
        self.text_item1 = BlockText(self, w, h)
        self.text_item2 = BlockText(self, w, h)
        self.text_item3 = BlockText(self, w, h)
        self.text_item4 = BlockText(self, w, h)
        self.parent.addItem(self.text_item0)
        self.parent.addItem(self.text_item1)
        self.parent.addItem(self.text_item2)
        self.parent.addItem(self.text_item3)
        self.parent.addItem(self.text_item4)
        self.visible_classes = visible_classes
        self.setAcceptHoverEvents(True)


    def mousePressEvent(self, event):
        self.moved = True
        if event.button() == Qt.MouseButton.LeftButton:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.start_x = self.x()
        super().mousePressEvent(event)



    def delete(self):
        self.parent.removeItem(self)
        self.parent.removeItem(self.text_item0)
        if hasattr(self, 'block'):
            self.db.delete_block(self.block)

    def bring_back(self):
        if self.isSelected():
            z_values = [item.zValue()  for item in self.collidingItems() if isinstance(item, BasicBlock)]
            if z_values:
                z = min(z_values) - 1
                self.setZValue(z)
                self.text_item0.setZValue(z+0.1)

    def bring_forward(self):
        z_values = [item.zValue()  for item in self.collidingItems() if isinstance(item, BasicBlock)]
        if z_values:
            z = max(z_values) + 1
            self.setZValue(z)
            self.text_item0.setZValue(z+0.1)

    def set_selectable(self, on:bool):
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, on)

    def set_movable(self, on:bool, five_min_h, top_bar_h):
        self.five_min_h = five_min_h
        self.top_bar_h = top_bar_h
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, on)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if not self.flags() & QGraphicsRectItem.ItemIsMovable:
            return


    def y_in_scene(self):
        return self.mapToScene(self.boundingRect()).boundingRect().y() 
    
    def mouseMoveEvent(self, event, show_tooltip=True):
        super().mouseMoveEvent(event)
        if self.isSelected() and self.flags() & QGraphicsRectItem.ItemIsMovable:
            # snap to grid
            x = self.start_x
            y = snap_position(self.y(), self.five_min_h)
            self.setPos(x, y)

            # correct if out of bounds
            while self.y_in_scene() + self.five_min_h/2 < self.top_bar_h:
                self.moveBy(0, self.five_min_h)
            while self.y_in_scene() + self.block.length*self.five_min_h > self.parent.height():
                self.moveBy(0, -self.five_min_h)

            self.bring_forward()

            # show tooltip
            start = (self.y_in_scene() - self.top_bar_h) // self.five_min_h + 1
            duration = self.block.length
            times = [start, start+duration]
            time = '-'.join([display_hour(t) for t in times])
            if self.block.length>=0:
                time += f' ({int(self.block.length)*5})'
            if show_tooltip:
                QToolTip.showText(event.screenPos(), time)

            # move text
            # self.recenter_text()

            # update database 
            self.db.update_block_start(self.block, start)


    def recenter_text(self, text_item=None, rect=None):
        if not rect:
            rect = self.rect()
        if not text_item:
            text_item = self.text_item0
        text_item.set_h(rect.height())
        text_item.shrink()
        text_item.setZValue(self.zValue()+0.1)
        text_item.setPos(rect.center().x() - text_item.boundingRect().width()/2,\
                            self.y_in_scene() + rect.height()/2 - text_item.boundingRect().height()/2)
        
    def other_subclasses_visible(self):
        my_class = self.block.parent().get_class()
        n = sum([1 for cl in self.visible_classes if cl.get_class() == my_class])
        return n > 1
    
    def lesson_names(self, lessons):
        return [
            (l.subject.full_name(), l.subject.short_full_name())
            if l.subject.my_class or (self.block.class_id and self.other_subclasses_visible())
            or settings.draw_blocks_full_width
            else (l.subject.name, l.subject.short_name)
            for l in lessons
        ]
    
    def set_filter(self, filter):
        self.filter = filter