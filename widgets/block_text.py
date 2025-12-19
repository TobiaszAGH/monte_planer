from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption


class BlockText(QGraphicsTextItem):
    def __init__(self, parent, w):
        super().__init__()
        self.contextMenuEvent = parent.contextMenuEvent
        self.bring_back = parent.bring_back
        self.bring_forward = parent.bring_forward
        option = QTextOption()
        option.setAlignment(Qt.AlignCenter)
        self.document().setDefaultTextOption(option)
        self.setTextWidth(w)
        self.w = w
        self.row_num = 0

    def shrink(self):
        if not self.row_num:
            return 
        font = self.font()
        size = font.pointSize()
        if self.text_too_big():
            self.shorten_names()
        while self.text_too_big() and size >=4:
            size -= 0.2
            font.setPointSizeF(size)
            self.setFont(font)

    def shorten_names(self) -> None:
        self.setHtml('<br>'.join([l[1] for l in self.lessons]))

    def text_too_big(self) -> bool:
        wrapping = self.document().begin().layout().lineCount() > self.row_num
        overflowing = self.boundingRect().width() > self.w
        return wrapping or overflowing
    
    def set_lessons(self, lessons):
        self.lessons = lessons
        self.row_num = len(lessons)
        self.setHtml('<br>'.join([l[0] for l in lessons]))

