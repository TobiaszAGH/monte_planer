from __future__ import annotations

from typing import List
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass



teacher_subject_table = Table(
    "teacher_subject_table",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True)
)


class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    subjects: Mapped[List[Subject]] = relationship(
        secondary=teacher_subject_table, back_populates="teachers"
    )

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    teachers: Mapped[List[Teacher]] = relationship(
        secondary=teacher_subject_table, back_populates="subjects"
    )
    

from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)
