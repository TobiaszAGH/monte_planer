from db_config import Base, student_subject
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

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

