from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QColor, QBrush
from .block import BasicBlock
from .add_lesson_dialog import AddLessonToBlockDialog
from .remove_lesson_dialog import RemoveLessonFromBlockDialog
from data import Class
from functions import contrast_ratio


class LessonBlock(BasicBlock):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)


    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)
        add_lesson_action = self.menu.addAction('Dodaj lekcję')
        add_lesson_action.triggered.connect(self.add_subject)
        remove_lesson_action = self.menu.addAction('Usuń lekcję')
        remove_lesson_action.triggered.connect(self.remove_lesson)
        action = self.menu.exec(event.globalPos())


    def add_subject(self):
        dialog = AddLessonToBlockDialog(self)
        ok = dialog.exec()
        if not ok:
            return False
        subject = dialog.subject_list.currentData()
        lesson = dialog.lesson_list.currentData()
        classroom = dialog.classroom_list.currentData()
        if subject and lesson:
            old_block: LessonBlock = lesson.block
                
            # update db
            self.db.update_lesson_classroom(lesson, classroom)
            self.db.add_lesson_to_block(lesson, self.block)
        
            # update visuals
            if old_block:
                old_block_item: LessonBlock = [bl for bl in self.parent.items() if isinstance(bl, LessonBlock) and bl.block==old_block][0]
                old_block_item.draw_lessons()
            self.draw_lessons()

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
        self.draw_lessons()

    def draw_lessons(self):
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

