from db_config import Base, subclass_customblock
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Subclass(Base):
    __tablename__ = 'subclasses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))
    students = relationship("Student", backref="subclass")
    subjects = relationship("Subject", backref="subclass")
    blocks = relationship("LessonBlockDB", backref="subclass")
    custom_blocks = relationship("CustomBlock", secondary=subclass_customblock, back_populates="subclasses")

    def full_name(self):
        return self.my_class.name + self.name
    
    def get_class(self):
        return self.my_class

