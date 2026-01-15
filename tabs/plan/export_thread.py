from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QFileDialog, QGraphicsTextItem, QApplication
from PyQt5.QtGui import QPixmap, QPainter
from pathlib import Path
from db_config import settings
from PyQt5.QtPrintSupport import QPrinter
import os
from progress_dialog import ProgressDialog
from collections.abc import Callable

class exportThread(QThread):
    result_ready = pyqtSignal(int)
    update_hidden_view = pyqtSignal([object, list])

    def __init__(self, plan, parent_folder):
        super().__init__()
        self.plan = plan
        self.parent_folder = parent_folder

    
    def run(self):
        # self.update_hidden_view.emit('foo', [4])
        parent_folder = self.parent_folder
        settings.alpha = 255 
        settings.hide_empty_blocks = True
        settings.draw_blocks_full_width = False
        settings.draw_custom_blocks = True
        settings.italicize_unlocked_lessons = False



        scene = self.plan.hidden_view.scene()
        rect = scene.sceneRect()

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPaperSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Landscape)


        pix = QPixmap(rect.size().toSize())
        for subclass in self.plan.db.all_subclasses():
            # self.plan.bar.next()
            path =  f'{parent_folder}/{subclass.full_name()}'
            os.makedirs(path, exist_ok=True)
            def filter_func(l):
                return l.subject.parent() in [subclass, subclass.my_class]
            self.update_hidden_view.emit(filter_func, [subclass])
            

            filename = f'{parent_folder}/{subclass.full_name()}/{subclass.full_name()}'
            # self.render(filename, pix, printer, scene)

            for student in subclass.students:
                filename = f'{parent_folder}/{subclass.full_name()}/{student.name}'
                def filter_func(l):
                    return student in l.subject.students
                self.update_hidden_view.emit(filter_func, [subclass])

                # self.render(filename, pix, printer, scene)

        settings.draw_custom_blocks = False
        settings.draw_blocks_full_width = True


        # os.makedirs(f'{parent_folder}/nauczyciele', exist_ok=True)
        # for teacher in self.plan.db.read_all_teachers():
        #     filename = f'{parent_folder}/nauczyciele/{teacher.name}'
        #     # self.plan.bar.next()
        #     # self.plan.bar.set_label(filename)
        #     def filter_func(l):
        #         return l.subject.teacher == teacher
        #     self.update_hidden_view.emit(filter_func, self.plan.db.all_subclasses())

        #     self.render(filename, pix, printer, scene)

        # os.makedirs(f'{parent_folder}/sale', exist_ok=True)
        # for classroom in self.plan.db.all_classrooms():
        #     filename = f'{parent_folder}/sale/{classroom.name}'
        #     # self.plan.bar.next()
        #     # self.plan.bar.set_label(filename)
        #     def filter_func(l):
        #         return l.classroom == classroom
        #     self.update_hidden_view.emit(filter_func, self.plan.db.all_subclasses())

        #     self.render(filename, pix, printer, scene)


                       
        settings.hide_empty_blocks = False
        settings.draw_blocks_full_width = False
        settings.draw_custom_blocks = True
        settings.italicize_unlocked_lessons = True
        self.plan.update_alpha(self.plan.alpha_slider.value())

        # self.plan.bar = None
        self.result_ready.emit(1)

    def render(self, filename, pix, printer, scene):
        pix.fill(Qt.white)
        painter = QPainter(pix)
        scene.render(painter)
        pix.save(filename + '.png', 'PNG', 100)
        painter.end()

        printer.setOutputFileName(filename + '.pdf')
        painter_pdf = QPainter(printer)
        scene.render(painter_pdf)
        painter_pdf.end()



    def render_scene_to_pixmap(self):
        self.plan.container.show()
        scene = self.plan.hidden_view.scene()
        for text in [i for i in scene.items() if isinstance(i, QGraphicsTextItem)]:
            text.ensureVisible()
        rect = scene.sceneRect()

        pix = QPixmap(rect.size().toSize())
        pix.fill(Qt.white)

        painter = QPainter(pix)
        scene.render(painter)
        painter.end()
        filename, _ = QFileDialog.getSaveFileName(self.plan, 'Eksportuj', 'self.plan.png')
        pix.save(filename, 'PNG', 100)
        self.plan.container.hide()
 


