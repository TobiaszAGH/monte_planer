from PyQt5.QtWidgets import QAction, QToolTip, QGraphicsRectItem
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter
from PyQt5.QtCore import Qt, QRectF
from .block import BasicBlock
from .add_lesson_dialog import AddLessonToBlockDialog
from .remove_lesson_dialog import RemoveLessonFromBlockDialog
from .manage_classrooms_dialog import ManageClassroomsDialog
from .block_text import BlockText
from functions import contrast_ratio
from db_config import settings


class LessonBlock(BasicBlock):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)
        self.text_items = {}
        # self.text_items = [BlockText(self, w, h) for n in range(]



    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)
        add_lesson_action =  QAction('Dodaj lekcję')
        self.menu.insertAction(self.remove_action, add_lesson_action)
        add_lesson_action.triggered.connect(self.add_subject)
        if len(self.block.lessons):
            manage_classrooms_action =  QAction('Zarządzaj salami')
            self.menu.insertAction(self.remove_action, manage_classrooms_action)
            manage_classrooms_action.triggered.connect(self.manage_classrooms)
            remove_lesson_action =  QAction('Usuń lekcję')
            self.menu.insertAction(self.remove_action, remove_lesson_action)
            remove_lesson_action.triggered.connect(self.remove_lesson)
        action = self.menu.exec(event.globalPos())


    def mouseMoveEvent(self, event):
        colliding_blocks = [bl for bl in self.collidingItems() if isinstance(bl, LessonBlock)]
        super().mouseMoveEvent(event, False)

        if self.isSelected() and self.flags() & QGraphicsRectItem.ItemIsMovable:
            collisions = self.draw_collisions()
            if collisions:
                QToolTip.showText(event.screenPos(), self.time() + '\n' + collisions)
            else:
                QToolTip.showText(event.screenPos(), self.time())
            colliding_blocks.extend([bl for bl in self.collidingItems() if isinstance(bl, LessonBlock)])
            for block in colliding_blocks:
                block.draw_collisions()

    def add_subject(self):
        dialog = AddLessonToBlockDialog(self)
        ok = dialog.exec()
        if not ok:
            return False
        subject = dialog.subject_list.currentData()
        lesson = dialog.lesson_list.currentData()
        classroom = dialog.classroom_list.currentData()
        if subject and lesson and classroom:
            old_block: LessonBlock = lesson.block
                
            # update db
            self.db.update_lesson_classroom(lesson, classroom)
            self.db.add_lesson_to_block(lesson, self.block)
        
            # update visuals
            if old_block:
                old_block_item: LessonBlock = [bl for bl in self.parent.items() if isinstance(bl, LessonBlock) and bl.block==old_block][0]
                old_block_item.draw_contents()
            self.draw_contents()

    def remove_lesson(self):
        if not self.block.lessons:
            return False
        if len(self.block.lessons) == 1:
            lesson = self.block.lessons[0]
        else:
            dialog = RemoveLessonFromBlockDialog(self.block.lessons)
            ok = dialog.exec()
            if not ok:
                return False
            lesson = dialog.list.currentData()
        self.db.remove_lesson_from_block(lesson)
        for block in self.collidingItems():
            if isinstance(block, LessonBlock):
                block.draw_collisions()
        self.draw_contents()

    def manage_classrooms(self):
        if not len(self.block.lessons):
            return
        ManageClassroomsDialog(self).exec()
        self.draw_contents()
        for item in self.collidingItems():
            if isinstance(item, LessonBlock):
                item.draw_collisions()

    def paint(self, painter, option, widget = ...):
        lessons = list(filter(self.filter, self.block.lessons))
        if settings.hide_empty_blocks and not len(lessons):
            self.hide()

        if self.block.my_class \
          and not len([l for l in lessons if not l.subject.basic]):
            rects = []
            r = self.rect()
            buckets = {sub_class:[] for sub_class in self.block.my_class.subclasses if sub_class in self.visible_classes}
            for lesson in lessons:
                buckets[lesson.subject.parent()].append(lesson)
            n_of_buckets = len(buckets)
            if not n_of_buckets:
                return
            
            width = r.width()/n_of_buckets
            height = r.height()
            y = r.top()
            for n in range(n_of_buckets):
                x = r.left()
                if settings.draw_blocks_full_width:
                    width = r.width()
                else:
                    x += width * n
                rects.append(QRectF(x, y, width, height))
        else:
            rects = [self.rect()]
            buckets = {self.block.subclass: lessons}

        for rect, subclass, lessons in zip(rects, buckets.keys(), buckets.values()):
            if settings.hide_empty_blocks and not len(lessons):
                continue
            # subclass, lessons = bucket
            colors = list(set([lesson.subject.color for lesson in lessons]))
            color = colors[0] if len(colors) == 1 else '#c0c0c0'
            color = QColor(color)
            # print(color)
            brush = QBrush(color)

            painter.fillRect(rect, brush)
            painter.drawRect(rect)

            try:
                text_item = self.text_items[subclass]
            except:
                text_item = BlockText(self, rect.width(), rect.height())
                self.text_items[subclass] = text_item

            text_item.set_h(rect.height())

            text_item.setZValue(self.zValue()+0.1)
            text_item.setPos(rect.center().x() - text_item.boundingRect().width()/2,\
                    rect.top() + rect.height()/2 - text_item.boundingRect().height()/2)
            # get correct suffixes
            lesson_names = self.lesson_names(lessons)
            self.lessons = zip(lesson_names, lessons)

            # correct color
            if contrast_ratio(color, QColor('black')) < 4.5:
                text_item.setDefaultTextColor(QColor('white'))
            else:
                text_item.setDefaultTextColor(QColor('black'))

            # write on screen
            text_item.set_lessons(lesson_names)
            text_item.add_classrooms('/'.join([l.classroom.name if l.classroom else '_' for l in lessons]))
            text_item.setZValue(self.zValue()+0.1)
            text_item.shrink()
        super().paint(painter, option, widget)
        


    def draw_contents(self):
        self.update()
    
    def draw_collisions(self):
        collisions = []
        for lesson in self.block.lessons:
            collisions.extend(self.db.lesson_collisions(lesson))

        collisions = '\n'.join(collisions)

        if collisions:
            self.setPen(QPen(QBrush(Qt.red),4))
            self.setToolTip(self.time() + '\n' + collisions)
        else:
            self.setPen(QPen())
            self.setToolTip(self.time())
        return collisions
    
    def time(self):
        return f'{self.block.print_time()} ({self.block.length*5})'
