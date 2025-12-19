from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table, Boolean
from string import ascii_lowercase
from typing import List
from functions import display_hour, shorten_name

def blank_data():
    return {
        'classes': {},
        'subjects': {},
        'teachers': {},
        'blocks': {}
    }

days = 'Pn Wt Śr Czw Pt'.split()

Base = declarative_base()

student_subject = Table(
    "student_subject",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    subclass_id = Column(Integer, ForeignKey('subclasses.id'))
    subjects = relationship("Subject", secondary=student_subject, back_populates="students")
    # class = 

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    students = relationship("Student", backref="my_class")
    subclasses = relationship("Subclass", backref="my_class")
    subjects = relationship("Subject", backref="my_class")
    blocks = relationship("Block", backref="my_class")

    def full_name(self):
        return self.name
    
    def get_class(self):
        return self

class Subclass(Base):
    __tablename__ = 'subclasses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    students = relationship("Student", backref="subclass")
    subjects = relationship("Subject", backref="subclass")
    blocks = relationship("Block", backref="subclass")

    def full_name(self):
        return self.my_class.name + self.name
    
    def get_class(self):
        return self.my_class

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    av1 = Column(Integer)
    av2 = Column(Integer)
    av3 = Column(Integer)
    av4 = Column(Integer)
    av5 = Column(Integer)
    subjects = relationship("Subject", backref='teacher')

    def __init__(self, name, av):
        self.name = name
        self.av1, self.av2, self.av3, self.av4, self.av5 = av 


class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    short_name = Column(String)
    class_id = Column(Integer, ForeignKey('classes.id'))
    subclass_id = Column(Integer, ForeignKey('subclasses.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    basic = Column(Boolean)
    color = Column(String)
    students = relationship("Student", secondary=student_subject, back_populates="subjects")
    lessons = relationship("Lesson", backref="subject")


    def parent(self):
        if self.my_class:
            return self.my_class
        if self.subclass:
            return self.subclass
        
    def full_name(self):
        if self.my_class:
            return self.name + ' R'
        else:
            return f'{self.name} {self.subclass.name.upper()}'
    
    def short_full_name(self):
        if self.my_class:
            return self.short_name + ' R'
        else:
            return f'{self.short_name} {self.subclass.name.upper()}'
    

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    block_id =  Column(Integer, ForeignKey('blocks.id'))

class Block(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False) # in 5 min blocks
    start = Column(Integer, nullable=False) # in 5 min blocks
    day = Column(Integer, nullable=False) # 0=mon, 1=tue etc.
    class_id = Column(Integer, ForeignKey('classes.id'))
    subclass_id = Column(Integer, ForeignKey('subclasses.id'))
    lessons = relationship("Lesson", backref="block")

    def parent(self):
        if self.my_class:
            return self.my_class
        if self.subclass:
            return self.subclass
        
    def print_time(self):
        return f'{display_hour(self.start)}-{display_hour(self.start+self.length)}'
    
    def print_full_time(self):
        return f'{days[self.day]} {self.print_time()}'

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

    # def teacher_names(self):
    #     return [t.name for t in self.session.query(Teacher).all()]
    
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
        student.subjects.append(subject)
        self.session.commit()

    def student_exists(self, name):
        student = self.session.query(Student).filter_by(name=name).first()
        return student.subclass.full_name() if student else None

    # subjects
    def create_subject(self, name, basic, my_sub_class) -> Subject:
        subject = Subject(name=name, basic=basic, color='#c0c0c0', short_name=shorten_name(name))
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

    def create_block(self, day:int, start:int, length:int, my_class) -> Block:
        if isinstance(my_class, Class):
            block = Block(day=day, start=start, length=length, my_class=my_class)
        else:
            block = Block(day=day, start=start, length=length, subclass=my_class)
        self.session.add(block)
        self.session.commit()
        return block

    def all_blocks(self) -> List[Block]:
        return self.session.query(Block).all()
    
    def delete_block(self, block):
        self.session.delete(block)
        self.session.commit()

    def update_block_start(self, block: Block, start: int):
        block.start = start
        self.session.commit()

    def add_lesson_to_block(self, lesson: Lesson, block: Block):
        block.lessons.append(lesson)
        lesson.block = block
        self.session.commit()

    def remove_lesson_from_block(self, lesson: Lesson):
        lesson.block = None
        self.session.commit()
