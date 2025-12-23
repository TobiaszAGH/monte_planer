from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption, QFont, QTextCursor, QTextCharFormat


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
        self.row_num = 0

    def shrink(self):
        doc = self.document()
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())  # reset formatting
        self.setFont(QFont())
        font = self.font()
        size = font.pointSize()
        if self.text_too_big() and self.lessons:
            self.shorten_names()
        while self.text_too_big() and size >=4:
            size -= 0.2
            font.setPointSizeF(size)
            self.setFont(font)

    def shorten_names(self) -> None:
        self.setHtml('<br>'.join([l[1] for l in self.lessons]) + '<br>' + self.classrooms)

    def text_too_big(self) -> bool:
        wrapping = self.document().begin().layout().lineCount() > self.row_num + 1
        overflowing = self.boundingRect().width() > self.w or self.boundingRect().height() > self.h
        return wrapping or overflowing
    
    def set_lessons(self, lessons):
        self.lessons = lessons
        self.row_num = len(lessons)
        self.setHtml('<br>'.join([l[0] for l in lessons]))

    def set_h(self, h):
        self.h = h

    def add_classrooms(self, classrooms: str):
        self.classrooms = classrooms
        self.setHtml(self.toHtml() + classrooms)

