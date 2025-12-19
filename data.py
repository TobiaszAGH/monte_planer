from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from string import ascii_lowercase
from typing import List
from functions import shorten_name
from db_config import Base
from models import *


class Data():
    def __init__(self):
        engine = create_engine("sqlite:///planer.db")
        Base.metadata.create_all(engine)
        DBsession = sessionmaker(bind=engine)
        self.session = DBsession()
        
    def table_names(self):
        return Base.metadata.tables.keys()
    

    # teachers
    def create_teacher(self, name, availability = [0]*5):
        print(availability)
        teacher = Teacher(name=name, av=availability)
        try:
            self.session.add(teacher)
            self.session.commit()
            return teacher
        except IntegrityError:
            self.session.rollback()
            raise IntegrityError('Taki nauczyciel już istnieje', '', '')
        
    def read_teacher_av(self, t: Teacher):
        return [t.av1, t.av2, t.av3, t.av4, t.av5]
        
    def update_teacher_av(self, t: Teacher, av):
        t.av1, t.av2, t.av3, t.av4, t.av5 = av
        self.session.commit()

    def update_teacher_name(self, t: Teacher, name):
        t.name = name
        self.session.commit()

    def read_all_teachers(self):
        return self.session.query(Teacher).order_by(Teacher.name).all()

    def delete_teacher(self, t):
        self.session.delete(t)
        self.session.commit()

    # classes
    def all_classes(self) -> List[Class]:
        return self.session.query(Class).all()

    def create_class(self, name: str) -> Class:
        subclass = Subclass(name='a')
        new_class = Class(name=name, subclasses=[subclass])
        self.session.add(subclass)
        self.session.add(new_class)
        self.session.commit()
        return new_class
    
    def delete_class(self, my_class: Class) -> None:
        for subclass in my_class.subclasses:
            self.delete_subclass(subclass)
        for subject in my_class.subjects:
            self.session.delete(subject)
        self.session.delete(my_class)
        self.session.commit()
    
    def create_subclass(self, my_class: Class) -> Subclass:
        names = [s.name for s in my_class.subclasses]
        name = ascii_lowercase[len(names)] 
        subclass = Subclass(name=name, class_id=my_class.id)
        self.session.add(subclass)
        self.session.commit()
        return subclass

    
    def delete_subclass(self, subclass: Subclass) -> None:
        my_class: Class = subclass.my_class
        for student in subclass.students:
            self.delete_student(student)
        for block in subclass.blocks:
            self.delete_block(block)
        for subject in subclass.subjects:
            self.delete_subject(subject)
        self.session.delete(subclass)
        self.session.commit()
        for name, subclass in zip(ascii_lowercase, my_class.subclasses):
            subclass.name = name
        # if only one subclass left, move its blocks to class
        if len(my_class.subclasses)==1:
            for block in my_class.subclasses[0].blocks:
                block.subclass=None
                block.my_class=my_class
        self.session.commit()


    # students
    def create_student(self, name, subclass:Subclass):
        student = Student(name=name, subclass=subclass, class_id=subclass.class_id)
        self.session.add(student)
        self.session.commit()
        return student
    
    def delete_student(self, student):
        self.session.delete(student)
        self.session.commit()

    def remove_subject_from_student(self, subject: Subject, student: Student):
        student.subjects.remove(subject)
        self.session.commit()

    def add_subject_to_student(self, subject: Subject, student: Student):
        if subject in student.subjects:
            return
        student.subjects.append(subject)
        self.session.commit()

    def student_exists(self, name):
        student = self.session.query(Student).filter_by(name=name).first()
        return student.subclass.full_name() if student else None

    # subjects
    def create_subject(self, name, basic, my_sub_class) -> Subject:
        # copy values if subject with same name exists or load deafaults
        same_name_subject = self.session.query(Subject).filter_by(name=name).first()
        if same_name_subject:
            color = same_name_subject.color
            teacher = same_name_subject.teacher
            short_name = same_name_subject.short_name
        else:
            color = '#c0c0c0'
            teacher = None
            short_name = shorten_name(name)
        subject = Subject(name=name, basic=basic, color=color, short_name=short_name, teacher=teacher)
        my_sub_class.subjects.append(subject)
        self.session.add(subject)
        self.session.commit()
        return subject
    
    def read_subjects_of_student(self, student: Student) -> List[Subject]:
        return student.subjects
    
    def update_subject_teacher(self, subject: Subject, teacher: Teacher) -> None:
        subject.teacher = teacher
        self.session.commit()

    def update_subject_short_name(self, subject: Subject, short_name: str) -> None:
        subject.short_name = short_name
        self.session.commit()

    def update_subject_color(self, subject: Subject, color: str) -> None:
        subject.color = color
        self.session.commit()

    def delete_subject(self, subject: Subject) -> None:
        self.session.delete(subject)
        self.session.commit()
    
    def create_lesson(self, length: int, subject: Subject) -> Lesson:
        lesson = Lesson(length=length, subject=subject)
        self.session.add(lesson)
        self.session.commit()
        return lesson
    
    def delete_lesson(self, lesson: Lesson) -> None:
        self.session.delete(lesson)
        self.session.commit()

    def create_block(self, day:int, start:int, length:int, my_class) -> LessonBlockDB:
        if isinstance(my_class, Class):
            block = LessonBlockDB(day=day, start=start, length=length, my_class=my_class)
        else:
            block = LessonBlockDB(day=day, start=start, length=length, subclass=my_class)
        self.session.add(block)
        self.session.commit()
        return block

    def all_lesson_blocks(self) -> List[LessonBlockDB]:
        return self.session.query(LessonBlockDB).all()
    
    def delete_block(self, block):
        self.session.delete(block)
        self.session.commit()

    def update_block_start(self, block: LessonBlockDB, start: int):
        block.start = start
        self.session.commit()

    def add_lesson_to_block(self, lesson: Lesson, block: LessonBlockDB):
        block.lessons.append(lesson)
        lesson.block = block
        self.session.commit()

    def remove_lesson_from_block(self, lesson: Lesson):
        lesson.block = None
        self.session.commit()

    def all_custom_blocks(self) -> List[CustomBlock]:
        return self.session.query(CustomBlock).all()

    def create_custom_block(self, day:int, start:int, length: int, subclasses: List[Subclass]):
        block = CustomBlock(day=day, start=start, length=length, subclasses=subclasses, color='#c0c0c0', text='')
        self.session.add(block)
        self.session.commit()
        return block
    
    def update_custom_block_color(self, block, color):
        block.color = color
        self.session.commit()

    def update_custom_block_text(self, block: CustomBlock, text):
        block.text = text
        self.session.commit()
    
    def all_blocks(self):
        return self.all_lesson_blocks().extend(self.all_custom_blocks)
