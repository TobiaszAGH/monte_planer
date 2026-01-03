from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, or_, and_
from string import ascii_lowercase
from typing import List
from functions import shorten_name
from db_config import Base
from models import *


class Data():
    def __init__(self, filename="planer.mtp"):
        engine = create_engine('sqlite:///' + filename)
        Base.metadata.create_all(engine)
        DBsession = sessionmaker(bind=engine)
        self.session = DBsession()
        
    def table_names(self):
        return Base.metadata.tables.keys()

    # teachers
    def create_teacher(self, name, availability = [0]*5):
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


    # subclasses
    def all_subclasses(self) -> List[Subclass]:
        return self.session.query(Subclass).join(Class).order_by(Class.order).order_by(Subclass.class_id).all()

    # classes
    def all_classes(self) -> List[Class]:
        return self.session.query(Class).order_by(Class.order).all()

    def create_class(self, name: str) -> Class:
        subclass = Subclass(name='a')
        classes = self.all_classes()
        order = classes[-1].order + 1 if classes else 1
        new_class = Class(name=name, subclasses=[subclass], order=order)
        self.session.add(subclass)
        self.session.add(new_class)
        self.session.commit()
        return new_class
    
    def update_class_order(self, class_: Class, order: int) -> None:
        class_.order = order
        self.session.commit()

    def update_class_name(self, class_: Class, name: str) -> None:
        class_.name = name
        self.session.commit()
    
    def delete_class(self, my_class: Class) -> None:
        for subclass in my_class.subclasses:
            self.delete_subclass(subclass)
        for subject in my_class.subjects:
            self.session.delete(subject)
        self.session.delete(my_class)
        self.session.commit()
    
    def create_subclass(self, my_class: Class) -> Subclass:
        names = [s.name for s in my_class.subclasses]
        last_subclass = my_class.subclasses[-1]
        name = ascii_lowercase[len(names)] 
        subclass = Subclass(name=name, class_id=my_class.id)
        for custom_block in self.all_custom_blocks():
            if last_subclass in custom_block.subclasses:
                custom_block.subclasses.append(subclass)
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
        for custom_block in subclass.custom_blocks:
            custom_block.subclasses.remove(subclass)
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

    def update_subject_is_basic(self, subject: Subject, basic: bool) -> None:
        subject.basic = basic
        self.session.commit()

    def update_subject_classroom(self, subject: Subject, classroom: Classroom) -> None:
        subject.required_classroom = classroom
        self.session.commit()

    def delete_subject(self, subject: Subject) -> None:
        for lesson in subject.lessons:
            self.session.delete(lesson)
        self.session.delete(subject)
        self.session.commit()
    

    # lessons
    def create_lesson(self, length: int, subject: Subject) -> Lesson:
        lesson = Lesson(length=length, subject=subject)
        self.session.add(lesson)
        self.session.commit()
        return lesson
    
    def all_lessons(self) -> List[Lesson]:
        return self.session.query(Lesson).all()
    
    def set_all_lessons_locked(self, locked=True) -> None:
        for lesson in self.session.query(Lesson).all():
            lesson.block_locked = locked
        self.session.commit()
    
    def update_lesson_classroom(self, lesson: Lesson, classroom: Classroom) -> None:
        lesson.classroom = classroom
        self.session.commit()

    def update_lesson_locked(self, lesson: Lesson, locked: bool) -> None:
        lesson.block_locked = locked
        self.session.commit()
    
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
    
    def clear_all_lesson_blocks(self, leave_locked=False):
        for lesson in self.session.query(Lesson).all():
            if lesson.block_locked and leave_locked:
                continue
            self.remove_lesson_from_block(lesson)
        self.session.commit()
    
    def lesson_block_collides_with(self, block:LessonBlockDB, blocks: List[LessonBlockDB]):
        # get all other blocks during the same day
        for block_2 in blocks:
            if block.start <= block_2.start < block.start+block.length \
              or block_2.start <= block.start < block_2.start + block_2.length:
                yield block

    
    def delete_block(self, block):
        self.session.delete(block)
        if hasattr(block, 'lessons'):
            for lesson in block.lessons:
                lesson.classroom = None
        self.session.commit()

    def update_block_start(self, block: LessonBlockDB, start: int):
        block.start = start
        self.session.commit()

    def add_lesson_to_block(self, lesson: Lesson, block: LessonBlockDB, lock=True):
        if not lesson :
            return False

        if block:
            lesson.block = block
            block.lessons.append(lesson)
            lesson.block_locked = lock
        else:
            self.remove_lesson_from_block(lesson)
        self.session.commit()

    def remove_lesson_from_block(self, lesson: Lesson):
        lesson.classroom = None
        lesson.block = None
        lesson.block_locked = False
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

    def delete_unplaceable_custom_blocks(self):
        for custom_block in self.all_custom_blocks():
            orders = [scl.my_class.order for scl in custom_block.subclasses]
            orders.sort()
            for i in range(0, len(orders)-1):
                if orders[i+1] - orders[i] > 1:
                    self.session.delete(custom_block)
                    self.session.commit()
                    break
    
    def all_blocks(self):
        blocks = self.all_lesson_blocks()
        blocks.extend(self.all_custom_blocks())
        return blocks
    

    # classrooms
    def all_classrooms(self) -> List[Classroom]:
        return self.session.query(Classroom).all()
    
    def create_classroom(self, name: str) -> Classroom:
        classroom = Classroom(name=name, capacity=15)
        self.session.add(classroom)
        self.session.commit()
        return classroom

    def update_classroom_capacity(self, classroom: Classroom, capacity: int) -> None:
        classroom.capacity = capacity
        self.session.commit()

    def delete_classroom(self, classroom: Classroom) -> None:
        self.session.delete(classroom)
        self.session.commit()

    def get_collisions_for_classroom_at_block(self, classroom: Classroom, block: LessonBlockDB) -> List[Lesson]:
        return self.session.query(Lesson).filter_by(classroom=classroom)\
                   .join(Lesson.block).filter(LessonBlockDB.day == block.day)\
                   .filter(or_(
                        LessonBlockDB.start.between(block.start, block.start+block.length),
                        and_(LessonBlockDB.start <= block.start, block.start <= LessonBlockDB.start+LessonBlockDB.length)
                    )).all() \
            if classroom else []

   
    def get_collisions_for_teacher_at_block(self, teacher: Teacher, block: LessonBlockDB) -> List[Lesson]:
        return self.session.query(Lesson) \
                    .join(Lesson.subject).filter_by(teacher=teacher) \
                    .join(Lesson.block).filter(LessonBlockDB.day == block.day) \
                    .filter(or_(
                        LessonBlockDB.start.between(block.start, block.start+block.length), 
                        and_(LessonBlockDB.start <= block.start, block.start <= LessonBlockDB.start+LessonBlockDB.length)
                    )).all() \
        if teacher else []
    
    
    def get_collisions_for_students_at_block(self, students: List[Student], block: LessonBlockDB) -> List[Lesson]:
        student_ids = [s.id for s in students]
        return self.session.query(Lesson) \
                    .join(Lesson.subject).filter(Subject.students.any(Student.id.in_(student_ids)))\
                    .join(Lesson.block).filter(LessonBlockDB.day == block.day)\
                    .filter(or_(
                        LessonBlockDB.start.between(block.start, block.start+block.length),
                        and_(LessonBlockDB.start <= block.start, block.start <= LessonBlockDB.start+LessonBlockDB.length)
                    )).all()
    
    def is_teacher_available(self, teacher: Teacher, block: LessonBlockDB) -> bool:
        if teacher is None:
            return True
        mask_start = int(block.start//6)
        mask_end = int((block.start+block.length-0.5)//6) + 1
        mask = 0
        for shift in range(mask_start, mask_end):
            mask |=  1 << shift
        return not(mask & ~teacher.__getattribute__(f'av{block.day+1}'))
    
    def lesson_collisions(self, lesson):
        subject = lesson.subject

        # students
        collisions = [
            f'{subject.get_name()}: Niektórzy uczniowie mają {les.name_and_time()}'
            for les in self.get_collisions_for_students_at_block(subject.students, lesson.block)
            if les is not lesson]
        
        # teacher
        collisions.extend([
            f'{subject.get_name()}: {subject.teacher.name} prowadzi {les.name_and_time()}'
            for les in self.get_collisions_for_teacher_at_block(subject.teacher, lesson.block)
            if les is not lesson])
        
        if subject.teacher and not self.is_teacher_available(subject.teacher, lesson.block):
            collisions.append(f'{subject.get_name()}: {subject.teacher.name} nie jest dostępny w tych godzinach')
        
        # classroom
        collisions.extend([
            f'{subject.get_name()}: {lesson.classroom.name} jest zajęte przez {les.name_and_time()}'
            for les in self.get_collisions_for_classroom_at_block(lesson.classroom, lesson.block)
            if les is not lesson])
        
        return collisions
    
    def classroom_collisions(self, classroom, block, lesson):
        subject = lesson.subject
        # other lesson is taking place in that classroom
        collisions = self.get_collisions_for_classroom_at_block(classroom, block)
        collisions = [l.name_and_time() for l in collisions if l is not lesson]

        # classroom is to small
        if classroom.capacity < len(subject.students):
            collisions.append('Sala jest za mała.')

        # other classroom is required
        if subject.required_classroom and subject.required_classroom!=classroom:
            collisions.append(f'{subject.name} musi odbywać się w {subject.required_classroom.name}')
        
        return collisions
        


 