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

    def filter(self, l):
        return True

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

    def get_colliding_blocks(self):
        rect = self.mapRectToScene(self.boundingRect())

        return [bl for bl in self.scene().items() \
                            if isinstance(bl, LessonBlock) \
                            and (rect.top() <= bl.boundingRect().top() <= rect.bottom() \
                            or rect.top() <= bl.boundingRect().bottom() <= rect.bottom())]
    

    def mouseMoveEvent(self, event):
        colliding_blocks = self.get_colliding_blocks()
        super().mouseMoveEvent(event, False)

        if self.isSelected() and self.flags() & QGraphicsRectItem.ItemIsMovable:
            collisions = self.draw_collisions()
            if collisions:
                QToolTip.showText(event.screenPos(), self.time() + '\n' + collisions)
            else:
                QToolTip.showText(event.screenPos(), self.time())
            colliding_blocks.extend(self.get_colliding_blocks())
            for block in colliding_blocks:
                block.draw_collisions()
        self.draw_contents()

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
            for n in range(5):
                self.__getattribute__(f'text_item{n}').setHtml('')
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
        super().paint(painter, option)
        if not hasattr(self, 'block'):
            return super().paint(painter, option)
        

        rects, buckets, colors = self.get_rects()
        for rect, color in zip(rects, colors):
            if not color:
                continue

            brush = QBrush(color)
            painter.fillRect(rect, brush)
            painter.drawRect(rect)

    def get_rects(self):
        lessons = list(filter(self.filter, self.block.lessons))
        if settings.hide_empty_blocks and not len(lessons):
            self.hide()
        show_full_subject_names = False

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
                if settings.draw_blocks_full_width:
                    rects.append(self.rect())
                else:
                    x = r.left()
                    x += width * n
                    rects.append(QRectF(x, y, width, height))
        else:
            rects = [self.rect()]
            buckets = {self.block.subclass: lessons}
            show_full_subject_names = True
        final_colors = []
        for rect, subclass, lessons in zip(rects, buckets.keys(), buckets.values()):
            if settings.hide_empty_blocks and not len(lessons):
                final_colors.append(None)
                continue
            # subclass, lessons = bucket
            colors = list(set([lesson.subject.color for lesson in lessons]))
            color = colors[0] if len(colors) == 1 else '#c0c0c0'
            color = QColor(color)
            color.setAlpha(settings.alpha)
            final_colors.append(color)
        return rects, buckets, final_colors

       
    def write(self, specify_class=False):
        n=0
        rects, buckets, colors = self.get_rects()
        for rect, subclass, lessons, color in zip(rects, buckets.keys(), buckets.values(), colors):
            if settings.hide_empty_blocks and not len(lessons):
                continue

            rect = self.mapRectToScene(rect)
            match(n):
                case 0:
                    text_item = self.text_item0
                case 1:
                    text_item = self.text_item1
                case 2: 
                    text_item = self.text_item2
                case 3:
                    text_item = self.text_item3
            n+=1
            
            text_item.set_h(rect.height())

            text_item.set_w(rect.width())

            # correct color
            if contrast_ratio(color, QColor('black')) < 4.5:
                text_item.setDefaultTextColor(QColor('white'))
            else:
                text_item.setDefaultTextColor(QColor('black'))

            # write on screen
            specify_subclass = len([l for l in lessons if not l.subject.basic]) or specify_class
            text_item.write_lessons(lessons, self.block.start, self.block.length, specify_class, specify_subclass)
            # recenter
            text_item.setZValue(self.zValue()+0.2)
            text_item.setPos(rect.center().x() - text_item.boundingRect().width()/2,\
                    rect.top() + rect.height()/2 - text_item.boundingRect().height()/2)
    

    def draw_contents(self):
        self.draw_collisions()
        self.write()
        self.update()
    
    def draw_collisions(self):
        collisions = []
        for lesson in self.block.lessons:
            collisions.extend(self.db.lesson_collisions(lesson))

        collisions = '\n'.join(collisions)

        if collisions:
            self.setPen(QPen(QBrush(Qt.red),4))
            # QToolTip.showText(self.mapRectToScene(self.boundingRect().topLeft().toPoint()), self.time() + '\n' + collisions)
            self.setToolTip(self.time() + '\n' + collisions)
        else:
            self.setPen(QPen())
            self.setToolTip(self.time())
        return collisions
    
    def time(self):
        return f'{self.block.print_time()} ({self.block.length*5})'
