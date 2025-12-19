from PyQt5.QtWidgets import QMenu
from widgets.block import Block
from widgets.add_lesson_dialog import AddLessonToBlockDialog
from widgets.remove_lesson_dialog import RemoveLessonFromBlockDialog


class LessonBlock(Block):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)


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
                old_block_item: Block = [bl for bl in self.parent.items() if isinstance(bl, Block) and bl.block==old_block][0]
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

