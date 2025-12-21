from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QInputDialog
from .block import BasicBlock
from functions import contrast_ratio

class CustomBlock(BasicBlock):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)

    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)
        remove_lesson_action = self.menu.addAction('Wybierz kolor')
        remove_lesson_action.triggered.connect(self.pick_color)
        remove_lesson_action = self.menu.addAction('Ustaw tekst')
        remove_lesson_action.triggered.connect(self.set_text)
        self.menu.exec(event.globalPos())
    
    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.block.color))
        if color.isValid():
            color.setAlpha(210)
            self.setBrush(color)
            self.db.update_custom_block_color(self.block, color.name())

            if contrast_ratio(color, QColor('black')) < 4.5:
                self.text_item.setDefaultTextColor(QColor('#ffffff'))

    def set_text(self):
        text, ok = QInputDialog.getText(None, 'Podaj tekst', 'Tekst:') 
        if ok:
            self.text_item.setHtml(text)
            self.recenter_text()
            self.db.update_custom_block_text(self.block, text)
