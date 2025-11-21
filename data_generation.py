from random import choice, randint, choices

names = ['Adam', 'Barłomiej', 'Celina', 'Damian', 'Eryk', 'Filip', 'Grzegorz', 'Henryk', 'Ignacy', 'Jeremiasz', 'Konrad']
surnames = ['Abacik', 'Babacik', 'Cabacik', 'Dabacik']
alphabet = 'abcdefghijklmnoprstuwz'


class Teacher:

    def __init__(self, name:str, availability:list[bool]):
        if len(availability)!=5:
            raise Exception('lenght of availability must equal 5')
        self.name = name
        self.availability = availability

    @classmethod
    def random(cls):
        return cls( f'{choice(names)} {choice(surnames)}', [randint(0,2)>0 for _ in range(5)])

    def is_available(self, day):
        return self.availability[day]
    
    def __str__(self):
        return f'{self.name}: {self.availability}'
    
class Student:
    def __init__(self):
        self.name = f'{choice(names)} {choice(alphabet.upper())}.'
        self.subjects = []

    def __str__(self):
        return f'{self.name}: {", ".join([f"{sub.name} ({sub.teacher.name})" for sub in self.subjects])}'

class Grade:
    def __init__(self, name, students):
        self.name = name
        self.students = students

    def __init__(self, name):
        self.name = name
        self.students = []
        for _ in range(randint(13,20)):
            self.students.append(Student())
        
    def __str__(self):
        str = f'Klasa: {self.name}'
        for student in self.students:
            str += f'\n{student}'
        return str

    def add_random_subjects(self, subjects):
        for student in self.students:
            student.subjects.extend(choices(subjects, k=randint(2,3)))
    
    def add_english(self, n):
        english_groups = [
            Subject(f'Angielski {i+1}', Teacher.random(), self, []) for i in range(n)
        ]
        for student in self.students:
            student.subjects.append(choice(english_groups))

    def add_basic(self):
        for student in self.students:
            student.subjects.extend([
                f'Polski {self.name} P',
                f"Matematyka {self.name} {'P' if randint(0,2) else 'R'}",
                f'Biologia {self.name}' if not randint(0,3) else f'Przyroda {self.name}',
                f'Katecheza {self.name}',
            ])
            if randint(0,1):
                student.subjects.append('Polski R')

class Subject:
    def __init__(self, name, teacher, grade, lesson_length):
        self.name = name
        self.teacher = teacher
        self.grade = grade
        lesson_length = lesson_length
    
    def __str__(self):
        return self.name


    

if __name__ == '__main__':
    grade_I = Grade('I')
    grade_II = Grade('II')
    grade_III = Grade('III')
    grade_IV = Grade('IV')
    # subject_names = ['Polski P', 'Polski R', 'Matematyka P', 'Matematyka R', 'Informatyka', 'Fizyka', *[f'Ang {n}' for n in range(1,3)]]
    # print(subject_names)
    rozszerzenia = ['Polski', 'Matematyka', 'Biologia', 'Historia', 'WOS', 'Chemia', 'Fizyka', 'Hiszpański', 'Historia Sztuki', 'Informatyka', 'Geografia']
    rozszerzenia = [(name, Teacher.random()) for name in rozszerzenia]
    rozszerzenia_I = [Subject(name, teacher, grade_I, []) for name, teacher in rozszerzenia]
    grade_I.add_english(3)
    grade_I.add_random_subjects(rozszerzenia_I)
    print(grade_I)