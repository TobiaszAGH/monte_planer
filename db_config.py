from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, Table


Base = declarative_base()

days = 'Pn Wt Śr Czw Pt'.split()

subclass_customblock = Table(
    "subclass_customblock",
    Base.metadata,
    Column("subclass_id", Integer, ForeignKey("subclasses.id"), primary_key=True),
    Column("customblock_id", Integer, ForeignKey("custom_blocks.id"), primary_key=True),
)

student_subject = Table(
    "student_subject",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id"), primary_key=True),
)
class Settings():
    def __init__(self):
        self.allow_creating_conflicts = False
        self.hide_empty_blocks = False
        self.draw_blocks_full_width = False
        self.draw_custom_blocks = True
        self.alpha = 255
        self.italicize_unlocked_lessons = True

settings = Settings()