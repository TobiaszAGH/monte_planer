from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption, QFont, QTextCursor, QTextCharFormat
from functions import display_hour
from typing import List
from data import Lesson
from db_config import settings


class BlockText(QGraphicsTextItem):
    def __init__(self, parent, w, h):
        super().__init__(parent)
        self.contextMenuEvent = parent.contextMenuEvent
        self.bring_back = parent.bring_back
        self.bring_forward = parent.bring_forward
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)
        self.document().setDefaultTextOption(option)
        self.setTextWidth(w)
        self.w = w
        self.h = h
        self.time = None
        self.classrooms = None
        self.lessons = []
        self.show_full_names = False

    def shrink(self):
        if not self.toHtml():
            return
        doc = self.document()
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())  # reset formatting
        self.setFont(QFont())
        font = self.font()
        font.setPointSize(8)
        size = font.pointSize()
        
        if self.text_too_big() and hasattr(self, 'lessons') and len(self.lessons):
            self.shorten_names()
        while self.text_too_big() and size >=4:
            size -= 0.2
            font.setPointSizeF(size)
            self.setFont(font)

    def shorten_names(self) -> None:
        lines = [l.subject.short_full_name() 
                 if self.show_full_names or settings.draw_blocks_full_width
                 else l.subject.short_name for l in self.lessons]
        if self.time:
            lines.append(self.time)
        if self.classrooms:
            lines.append(self.classrooms)
        self.setHtml('<br>'.join(lines))


    def set_show_full_names(self, show):
        self.show_full_names = show


    def is_overflowing_h(self):
        return self.boundingRect().width() > self.w 

    def is_wrapping(self):
        row_num = self.toPlainText().count('\n') + 1
        doc = self.document()

        block = doc.firstBlock()
        count = 0

        while block.isValid():
            layout = block.layout()
            if layout is not None:
                count += layout.lineCount()
            block = block.next()

        return count > row_num
 


    def text_too_big(self) -> bool:
        # print(self.toPlainText())
        overflowing = self.boundingRect().width() > self.w or self.boundingRect().height() > self.h
        return self.is_wrapping() or overflowing
    
    def set_lessons(self, lessons):
        self.lessons: List[Lesson] = lessons
        self.update_text()

    def set_h(self, h):
        self.h = h

    def add_classrooms(self, classrooms: str):
        self.classrooms = classrooms
        self.update_text()

    def add_time(self, start, length):
        self.time = f'{display_hour(start)}-{display_hour(start+length)}'
        self.update_text()

    def update_text(self):
        lines = [l.subject.full_name() 
                 if self.show_full_names or settings.draw_blocks_full_width
                 else l.subject.name for l in self.lessons]
        if self.time:
            lines.append(self.time)
        if self.classrooms:
            lines.append(self.classrooms)
        self.setHtml('<br>'.join(lines))

    def set_custom_text(self, text):
        self.setHtml(text)

