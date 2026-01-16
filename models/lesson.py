from db_config import Base
from sqlalchemy import Column, Integer, ForeignKey, Boolean

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    block_id =  Column(Integer, ForeignKey('blocks.id'))
    classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    block_locked = Column(Boolean)
    classroom_locked = Column(Boolean)

    def name_and_time(self):
        return f'{self.subject.get_name()} o {self.block.print_time() if self.block else "(nieprzypisany)"}'

