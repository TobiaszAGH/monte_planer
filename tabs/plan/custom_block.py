from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog, QInputDialog, QLineEdit, QAction
from .block import BasicBlock
from functions import contrast_ratio

class CustomBlock(BasicBlock):
    def __init__(self, x, y, w, h, parent, db, visible_classes):
        super().__init__(x, y, w, h, parent, db, visible_classes)

    def contextMenuEvent(self, event):
        super().contextMenuEvent(event)
        pick_color_action = QAction('Wybierz kolor')
        pick_color_action.triggered.connect(self.pick_color)
        self.menu.insertAction(self.remove_action, pick_color_action)
        set_text_action = QAction('Ustaw tekst')
        set_text_action.triggered.connect(self.set_text)
        self.menu.insertAction(self.remove_action, set_text_action)
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
        placeholder = self.text_item.toPlainText().replace('\n', '<br>')
        text, ok = QInputDialog.getText(None, 'Podaj tekst', 'Tekst:', QLineEdit.Normal, placeholder) 
        if ok:
            self.text_item.set_custom_text(text)
            self.recenter_text()
            self.db.update_custom_block_text(self.block, text)

    def draw_contents(self):

        color = QColor(self.block.color)
        color.setAlpha(210)
        self.setBrush(color)
        self.text_item.set_custom_text(self.block.text)
        if contrast_ratio(color, QColor('black')) < 4.5:
            self.text_item.setDefaultTextColor(QColor('#ffffff'))
        self.recenter_text()