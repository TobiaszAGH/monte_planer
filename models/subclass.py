from db_config import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

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

