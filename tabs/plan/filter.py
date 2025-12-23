from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QPushButton, QGridLayout, QStackedLayout, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt
from .mode_btn import ModeBtn
from data import Class, Data
from db_config import settings

class FilterWidget(QWidget):
    def __init__(self, parent, view, tool_add_custom):
        super().__init__(parent)
        self.view = view
        self.db: Data = parent.db
        self.tool_add_custom = tool_add_custom

        main_layout = QGridLayout()
        self.setLayout(main_layout)
        main_layout.setColumnStretch(0,1)
        main_layout.setColumnStretch(1,2)

        filter_selection = QComboBox()
        items = 'Klasy Uczniowie Nauczyciele Sale'.split()
        filter_selection.addItems(items)
        filter_selection.currentIndexChanged.connect(self.select_filter)
        main_layout.addWidget(filter_selection, 0, 0)

        self.stacked = QStackedWidget()
        self.stacked.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        main_layout.addWidget(self.stacked, 0, 1)

        # classes
        self.class_filter = QWidget()
        self.class_filter.setLayout(QHBoxLayout())
        self.stacked.layout().addWidget(self.class_filter)

        # students
        self.student_filter = QWidget()
        self.student_filter.setLayout(QHBoxLayout())
        self.student_class_selection = QComboBox()
        self.student_filter.layout().addWidget(self.student_class_selection)
        self.student_list = QComboBox()
        self.student_filter.layout().addWidget(self.student_list)
        self.student_class_selection.currentTextChanged.connect(self.load_students)
        self.student_list.currentIndexChanged.connect(self.update_filter)
        self.stacked.layout().addWidget(self.student_filter)

        # teachers
        self.teacher_filter = QWidget()
        self.teacher_filter.setLayout(QHBoxLayout())
        self.teacher_list = QComboBox()
        self.teacher_filter.layout().addWidget(self.teacher_list)
        self.teacher_list.currentIndexChanged.connect(self.update_filter)
        self.stacked.layout().addWidget(self.teacher_filter)

        # classrooms
        self.classroom_filter = QWidget()
        self.classroom_filter.setLayout(QHBoxLayout())
        self.classroom_list = QComboBox()
        self.classroom_filter.layout().addWidget(self.classroom_list) 
        self.classroom_list.currentIndexChanged.connect(self.update_filter)
        self.stacked.layout().addWidget(self.classroom_filter)



    
    def filter_btn_clicked(self):
        self.tool_add_custom.uncheck()
        self.view.set_mode('normal')
        self.update_filter()

    def update_class_filter(self):
        settings.hide_empty_blocks = False
        settings.draw_blocks_full_width = False
        settings.draw_custom_blocks = True
        display_names = [
            button.my_class
            for button in self.findChildren(QPushButton)
            if button.isChecked() and hasattr(button, 'my_class')
        ]
        def filter(l):
            return l.subject.subclass in display_names \
                or l.subject.my_class
        return display_names, filter

    def update_student_filter(self):
        settings.hide_empty_blocks = True
        settings.draw_blocks_full_width = True
        settings.draw_custom_blocks = True
        student = self.student_list.currentData()
        if not student:
            return None, None
        def filter(l):
            return l.subject in student.subjects
        return [student.subclass], filter
    
    def update_teacher_filter(self):
        settings.hide_empty_blocks = True
        settings.draw_blocks_full_width = True
        settings.draw_custom_blocks = False
        teacher = self.teacher_list.currentData()
        if not teacher:
            return None, None
        classes = self.db.all_subclasses()
        def filter(l):
            return l.subject.teacher == teacher
        return classes, filter
    
    def update_classroom_filter(self):
        settings.hide_empty_blocks = True
        settings.draw_blocks_full_width = True
        settings.draw_custom_blocks = False
        classroom = self.classroom_list.currentData()
        if not classroom:
            return None, None
        classes = self.db.all_subclasses()
        def filter(l):
            return l.classroom == classroom
        return classes, filter


    def update_filter(self):
        index = self.stacked.currentIndex()
        filters = [
            self.update_class_filter,
            self.update_student_filter,
            self.update_teacher_filter,
            self.update_classroom_filter
        ]
        if len(filters) < index + 1:
            return
        classes, curr_filter = filters[index]()
        if curr_filter is None:
            return 
        self.view.set_classes(classes)
        self.view.filter_func = curr_filter
        self.view.draw()

    def select_filter(self, index):
        self.stacked.setCurrentIndex(index)
        self.update_filter()

    def load_students(self):
        subclass = self.student_class_selection.currentData()
        if not subclass:
            return
        self.student_list.clear()
        for student in subclass.students:
            self.student_list.addItem(student.name, student)

    def load_data(self):
        self.classes = self.db.all_subclasses()
            
        for widget in self.findChildren(QPushButton):
            widget.deleteLater()
        self.student_class_selection.clear()
        self.teacher_list.clear()
        self.classroom_list.clear()

        for index, my_class in enumerate(self.classes):
            self.student_class_selection.addItem(my_class.full_name(), my_class)
            button = QPushButton(my_class.full_name())
            button.setCheckable(True)
            button.setChecked(True)
            button.my_class = my_class
            button.clicked.connect(self.filter_btn_clicked)
            self.class_filter.layout().insertWidget(index, button)

        for teacher in self.db.read_all_teachers():
            self.teacher_list.addItem(teacher.name, teacher)

        for classroom in self.db.all_classrooms():
            self.classroom_list.addItem(classroom.name, classroom)



