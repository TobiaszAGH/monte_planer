from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog
from widgets.block import BasicBlock

class CustomBlock(BasicBlock):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)

    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)
        remove_lesson_action = self.menu.addAction('Wybierz kolor')
        remove_lesson_action.triggered.connect(self.pick_color)
        self.menu.exec(event.globalPos())
    
    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.block.color))
        if color.isValid():
            self.setBrush(color)
            self.db.update_custom_block_color(self.block, color.name())