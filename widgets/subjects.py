from PyQt6.QtWidgets import QWidget
from db import engine, Subject
from sqlalchemy.orm import Session

class SubjectsWidget(QWidget):
    def __init__(self):
        super().__init__()
        with Session(engine) as session:
            subjects_list = session.query(Subject).all()
        print(subjects_list)
