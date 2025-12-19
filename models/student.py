from db_config import Base, student_subject
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    subclass_id = Column(Integer, ForeignKey('subclasses.id'))
    subjects = relationship("Subject", secondary=student_subject, back_populates="students")