from db_config import Base, days
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from functions import display_hour

class LessonBlockDB(Base):
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
    
    def __str__(self):
        return self.print_full_time()
    
    def print_full_time(self):
        return f'{days[self.day]} {self.print_time()}'
    
   