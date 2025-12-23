from PyQt5.QtWidgets import QAction, QToolTip, QGraphicsRectItem
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt
from .block import BasicBlock
from .add_lesson_dialog import AddLessonToBlockDialog
from .remove_lesson_dialog import RemoveLessonFromBlockDialog
from .manage_classrooms_dialog import ManageClassroomsDialog
from data import Class
from functions import contrast_ratio


class LessonBlock(BasicBlock):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)


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
            dialog = RemoveLessonFromBlockDialog(self.lessons)
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

    def draw_contents(self):
        # pick which lessons to draw
        lessons = [l for l in self.block.lessons 
                   if isinstance(l.subject.parent(), Class) 
                   or l.subject.parent() in self.visible_classes
                   or len(l.subject.parent().get_class().subclasses) == 1]
        
        classrooms = '/'.join([l.classroom.name if l.classroom else '_'
                      for l in lessons])

        # pick background color
        color = lessons[0].subject.color if len(lessons) == 1 else '#c0c0c0'
        color = QColor(color)
        color.setAlpha(210)
        self.setBrush(QBrush(color))

        # pick contrasting text color
        if contrast_ratio(color, QColor('black')) < 4.5:
            self.text_item.setDefaultTextColor(QColor('#ffffff'))
        else:
            self.text_item.setDefaultTextColor(QColor('black'))

        # get correct suffixes
        lesson_names = self.lesson_names(lessons)
        self.lessons = zip(lesson_names, lessons)

        # write on screen
        self.text_item.set_lessons(lesson_names)
        self.text_item.add_classrooms(classrooms)
        self.text_item.setZValue(self.zValue()+0.1)

        self.recenter_text()
        
        self.draw_collisions()
        
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
