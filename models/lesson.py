from db_config import Base
from sqlalchemy import Column, Integer, ForeignKey

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    block_id =  Column(Integer, ForeignKey('blocks.id'))

