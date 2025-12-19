from db_config import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    students = relationship("Student", backref="my_class")
    subclasses = relationship("Subclass", backref="my_class")
    subjects = relationship("Subject", backref="my_class")
    blocks = relationship("LessonBlockDB", backref="my_class")

    def full_name(self):
        return self.name
    
    def get_class(self):
        return self

