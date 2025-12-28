from db_config import Base, student_subject, settings
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    short_name = Column(String)
    class_id = Column(Integer, ForeignKey('classes.id'))
    subclass_id = Column(Integer, ForeignKey('subclasses.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    basic = Column(Boolean)
    color = Column(String)
    students = relationship("Student", secondary=student_subject, back_populates="subjects")
    lessons = relationship("Lesson", backref="subject")


    def parent(self):
        if self.my_class:
            return self.my_class
        if self.subclass:
            return self.subclass
        
    def class_name(self):
        return self.my_class.name if self.my_class else self.subclass.my_class.name

    def get_name(self):
        return f'{self.name}' + (' R' if self.my_class else '')
    
    def get_short_name(self):
        return f'{self.short_name}' + (' R' if self.my_class else '')
        
    def full_name(self, full_subclass_name = False):
        if self.my_class:
            return f'{self.name} {self.my_class.name if settings.draw_blocks_full_width else ""} R'
        else:
            return f'{self.name} {self.subclass.full_name() if full_subclass_name or settings.draw_blocks_full_width else self.subclass.name.upper()}'
    
    def short_full_name(self, full_subclass_name = False):
        if self.my_class:
            return self.short_name + ' R'
        else:
            return f'{self.short_name} {self.subclass.full_name() if full_subclass_name or settings.draw_blocks_full_width else self.subclass.name.upper()}'
        
    def get_name(self, short=False, show_class_name = False, show_subclass_name = False):
        name = self.short_name if short else self.name
        class_name = ''
        if show_class_name:
            class_name += self.class_name()
        is_only_subclass = len(self.my_class.subclasses if self.my_class else self.subclass.my_class.subclasses) == 1
        if show_subclass_name:
            class_name += 'R' if self.my_class else \
                (self.subclass.name.upper() if not is_only_subclass else '')
        if class_name:
            name += ' ' + class_name
        return name
        
        
    

