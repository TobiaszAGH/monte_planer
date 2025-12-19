from db_config import Base, days, subclass_customblock
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from functions import display_hour

class CustomBlock(Base):
    __tablename__ = 'custom_blocks'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False) # in 5 min blocks
    start = Column(Integer, nullable=False) # in 5 min blocks
    day = Column(Integer, nullable=False) # 0=mon, 1=tue etc.
    class_id = Column(Integer, ForeignKey('classes.id'))
    subclasses = relationship("Subclass", secondary=subclass_customblock, back_populates="custom_blocks")

    # def parent(self):
    #     if self.my_class:
    #         return self.my_class
    #     if self.subclass:
    #         return self.subclass
        
    def print_time(self):
        return f'{display_hour(self.start)}-{display_hour(self.start+self.length)}'
    
    def print_full_time(self):
        return f'{days[self.day]} {self.print_time()}'

