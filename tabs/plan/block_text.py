from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption, QFont, QTextCursor, QTextCharFormat
from functions import display_hour


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

    def shrink(self):
        if not self.toHtml():
            return
        doc = self.document()
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())  # reset formatting
        self.setFont(QFont())
        # print(self.toPlainText())
        font = self.font()
        size = font.pointSize()
        if self.text_too_big() and hasattr(self, 'lessons') and self.lessons:
            self.shorten_names()
        while self.text_too_big() and size >=4:
            size -= 0.2
            font.setPointSizeF(size)
            self.setFont(font)

    def shorten_names(self) -> None:
        self.setHtml('<br>'.join([l[1] for l in self.lessons]) + '<br>' + self.time + '<br>' + self.classrooms)

    def text_too_big(self) -> bool:
        # print(self.toPlainText())
        row_num = self.toPlainText().count('\n') + 1
        doc = self.document()

        block = doc.firstBlock()
        count = 0

        while block.isValid():
            layout = block.layout()
            if layout is not None:
                count += layout.lineCount()
            block = block.next()

        wrapping = count > row_num
        overflowing = self.boundingRect().width() > self.w or self.boundingRect().height() > self.h
        return wrapping or overflowing
    
    def set_lessons(self, lessons):
        self.lessons = lessons
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
        lines = [l[0] for l in self.lessons]
        if self.time:
            lines.append(self.time)
        if self.classrooms:
            lines.append(self.classrooms)
        self.setHtml('<br>'.join(lines))

    def set_custom_text(self, text):
        self.setHtml(text)

