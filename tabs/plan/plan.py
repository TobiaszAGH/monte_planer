from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog,\
      QGraphicsTextItem, QStyleOptionGraphicsItem, QStackedWidget
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPainter, QTransform, QPixmap
from PyQt5.QtCore import Qt
from data import Data
from .mode_btn import ModeBtn
from .plan_view import MyView
from.filter import FilterWidget
from db_config import settings
import os
        

class PlanWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.db: Data = parent.db
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)




        toolbar = QWidget()
        toolbar.setLayout(QHBoxLayout())
        toolbar.layout().setContentsMargins(10,0,10,5)

        # modes
        self.tool_add_block = ModeBtn("Nowy blok zajęciowy", self.set_mode_new, toolbar)
        toolbar.layout().addWidget(self.tool_add_block)
        self.tool_move_block = ModeBtn("Przesuwanie", self.set_mode_move ,toolbar)
        toolbar.layout().addWidget(self.tool_move_block)
        self.tool_add_custom = ModeBtn("Nowy blok", self.set_mode_new_custom ,toolbar)
        toolbar.layout().addWidget(self.tool_add_custom)

        # scale
        toolbar.layout().addWidget(QLabel('Skala:'))
        self.scale_slider = QSlider(Qt.Horizontal, self)
        self.scale_slider.setMaximumWidth(150)
        self.scale_slider.setMinimum(100)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setSingleStep(10)
        self.scale_slider.setPageStep(50)
        self.scale_slider.setTickPosition(QSlider.TicksAbove | QSlider.TicksBelow)
        self.scale_slider.setTickInterval(50)
        self.scale_slider.valueChanged.connect(self.update_scale)
        toolbar.layout().addWidget(self.scale_slider)
        self.scale_label = QLabel('100%', self.scale_slider)
        toolbar.layout().addWidget(self.scale_label)

        # alpha
        toolbar.layout().addWidget(QLabel('Przeźroczystość:'))
        self.alpha_slider = QSlider(Qt.Horizontal, self)
        self.alpha_slider.setMaximumWidth(150)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(128)
        self.alpha_slider.setSingleStep(5)
        self.alpha_slider.setPageStep(25)
        self.alpha_slider.setTickPosition(QSlider.TicksAbove | QSlider.TicksBelow)
        self.alpha_slider.setTickInterval(32)
        self.alpha_slider.valueChanged.connect(self.update_alpha)
        toolbar.layout().addWidget(self.alpha_slider)
        self.alpha_label = QLabel('0%')
        toolbar.layout().addWidget(self.alpha_label)

 
        toolbar.layout().addStretch()

        export_btn = QPushButton('Eksportuj')
        toolbar.layout().addWidget(export_btn)
        export_btn.clicked.connect(self.render_plans_for_students)

        self.view = MyView(self)
        self.hidden_view = MyView(self)
        self.class_filter = FilterWidget(self, self.view, self.tool_add_custom)
        
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_DontShowOnScreen, True)
        conlayout = QVBoxLayout(self.container)
        conlayout.addWidget(self.hidden_view)

        self.container.show()
        self.hidden_view.resize(2970, 2100)
        self.container.hide()

        layout.addWidget(self.class_filter)
        layout.addWidget(toolbar)
        layout.addWidget(self.view)
        self.load_data(self.db)

    def render_plans_for_students(self):
        
        settings.hide_empty_blocks = True
        settings.draw_blocks_full_width = False
        settings.draw_custom_blocks = True

        scene = self.hidden_view.scene()
        parent_folder = QFileDialog.getExistingDirectory(self, 'Wybierz folder')
        rect = scene.sceneRect()

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPaperSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Landscape)


        pix = QPixmap(rect.size().toSize())
        for subclass in self.db.all_subclasses():
            os.makedirs(f'{parent_folder}/{subclass.full_name()}', exist_ok=True)
            def filter_func(l):
                return l.subject.parent() in [subclass, subclass.my_class]
            self.hidden_view.filter_func = filter_func
            self.hidden_view.set_classes([subclass])
            self.hidden_view.draw()
            self.hidden_view.narrow_overlapping_blocks()

            filename = f'{parent_folder}/{subclass.full_name()}/{subclass.full_name()}'
            self.render(filename, pix, printer, scene)

            for student in subclass.students:
                filename = f'{parent_folder}/{subclass.full_name()}/{student.name}'
                def filter_func(l):
                    return student in l.subject.students
                self.hidden_view.filter_func = filter_func
                self.hidden_view.set_classes([subclass])
                self.hidden_view.draw()

                self.render(filename, pix, printer, scene)

        settings.draw_custom_blocks = False
        settings.draw_blocks_full_width = True

        os.makedirs(f'{parent_folder}/nauczyciele', exist_ok=True)
        for teacher in self.db.read_all_teachers():
            filename = f'{parent_folder}/nauczyciele/{teacher.name}'
            def filter_func(l):
                return l.subject.teacher == teacher
            self.hidden_view.filter_func = filter_func
            self.hidden_view.set_classes(self.db.all_subclasses())
            self.hidden_view.draw()

            self.render(filename, pix, printer, scene)

        os.makedirs(f'{parent_folder}/sale', exist_ok=True)
        for classroom in self.db.all_classrooms():
            filename = f'{parent_folder}/sale/{classroom.name}'
            def filter_func(l):
                return l.classroom == classroom
            self.hidden_view.filter_func = filter_func
            self.hidden_view.set_classes(self.db.all_subclasses())
            self.hidden_view.draw()

            self.render(filename, pix, printer, scene)


                       
        settings.hide_empty_blocks = False
        settings.draw_blocks_full_width = False
        settings.draw_custom_blocks = True

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
        self.container.show()
        scene = self.hidden_view.scene()
        for text in [i for i in scene.items() if isinstance(i, QGraphicsTextItem)]:
            text.ensureVisible()
        rect = scene.sceneRect()

        pix = QPixmap(rect.size().toSize())
        pix.fill(Qt.white)

        painter = QPainter(pix)
        scene.render(painter)
        painter.end()
        filename, _ = QFileDialog.getSaveFileName(self, 'Eksportuj', 'plan.png')
        pix.save(filename, 'PNG', 100)
        self.container.hide()
 


    def update_scale(self, value):
        self.scale_label.setText(f'{value}%')
        self.view.resetTransform()
        self.view.scale(value/100, value/100)
        
    def set_mode_new(self, checked):
        if checked:
            self.class_filter.go_to_class_filter()
            self.view.set_mode('new')
        else:
            self.view.set_mode('normal')

    def set_mode_new_custom(self, checked):
        if checked:
            self.class_filter.go_to_class_filter()
            self.view.set_mode('new_custom')
            for button in self.class_filter.findChildren(QPushButton):
                button.setChecked(True)
            self.class_filter.update_class_filter() 
        else:
            self.view.set_mode('normal')
    
    def set_mode_move(self, checked):
        if checked:
            self.class_filter.go_to_class_filter()
            self.view.set_mode('move')
        else:
            self.view.set_mode('normal')

    def uncheck_all_modes(self):
        self.tool_add_block.uncheck()
        self.tool_add_custom.uncheck()
        self.tool_move_block.uncheck()
    
    def update_alpha(self, value):
        alpha = 255 - value
        settings.alpha = alpha
        percent = int(value/255*100)
        self.alpha_label.setText(f'{percent}%')
        self.view.draw()


    def load_data(self, db):
        self.db = db
        self.class_filter.load_data(db)
        self.view.load_data(db)
        self.hidden_view.load_data(db)
        if self.class_filter.filter_selection.currentText() == 'Klasy':
            self.view.set_classes(self.class_filter.classes)
            self.view.draw()
            self.hidden_view.set_classes(self.class_filter.classes)
            self.hidden_view.draw()
