from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, BLOB
# from sqlite3 import IntegrityError
from struct import pack
def blank_data():
    return {
        'classes': {},
        'subjects': {},
        'teachers': {},
        'blocks': {}
    }


Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    # class = 

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    students = relationship("Student", backref="class")

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    av1 = Column(Integer)
    av2 = Column(Integer)
    av3 = Column(Integer)
    av4 = Column(Integer)
    av5 = Column(Integer)
    # availability = [av1, av2, av3, av4, av5]

    # def __init__(self, name):
    #     self.name = name
    #     self.av1, self.av2, self.av3, self.av4, self.av5 = 65536, 65536, 65536, 65536, 65536

    def __init__(self, name, av):
        self.name = name
        self.av1, self.av2, self.av3, self.av4, self.av5 = av 


class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
class Data():
    def __init__(self):
        engine = create_engine("sqlite:///planer.db")
        Base.metadata.create_all(engine)
        DBsession = sessionmaker(bind=engine)
        self.session = DBsession()
        
    def table_names(self):
        return Base.metadata.tables.keys()
    
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
        
    def get_teacher_av(self, t: Teacher):
        return [t.av1, t.av2, t.av3, t.av4, t.av5]
        
    def update_teacher_av(self, t: Teacher, av):
        t.av1, t.av2, t.av3, t.av4, t.av5 = av
        self.session.commit()

    def update_teacher_name(self, t: Teacher, name):
        t.name = name
        self.session.commit()

    def teacher_names(self):
        return [t.name for t in self.session.query(Teacher).all()]
    
    def all_teachers(self):
        return self.session.query(Teacher).order_by(Teacher.name).all()

    def remove_teacher(self, t):
        self.session.delete(t)
        self.session.commit()