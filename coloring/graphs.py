from networkx import Graph
from itertools import combinations
from data import Data, Class, LessonBlockDB, Subject

def generate_lesson_graph(db: Data):
    graph = Graph()
    labels = {}

    # create subject graph
    for class_ in db.all_classes():
        # find all subjects in class and subclasses
        total_subjects = []
        total_subjects.extend(class_.subjects)
        for subclass in class_.subclasses:
            total_subjects.extend(subclass.subjects)

        graph.add_nodes_from(total_subjects)
        for pair in combinations(total_subjects, 2):
            for student in pair[0].students:
                if student in pair[1].students:
                    graph.add_edge(*pair)
                    break
    for pair in combinations(graph.nodes, 2):
        if pair[0].teacher == pair[1].teacher and pair[0].teacher is not None:
            graph.add_edge(*pair)
            continue
    
    feasible_blocks = {}
    for subject in db.session.query(Subject).all():
        for lesson in subject.lessons:
            feasible_blocks[lesson] = []
            for block in db.all_lesson_blocks():
                # wrong length
                if block.length*5 != lesson.length:
                    continue
                # teacher doesn't work at that time
                if not db.is_teacher_available(lesson.subject.teacher, block):
                    continue
                # block is in the wrong class
                possible_sub_classes = [block.parent()]
                if isinstance(possible_sub_classes[0], Class):
                    possible_sub_classes.extend(block.parent().subclasses)
                if lesson.subject.parent() not in possible_sub_classes:
                    continue
                # else block is feasible
                feasible_blocks[lesson].append(block)
            # if there is no possible blocks dont put it in graph
            if len(feasible_blocks[lesson]) == 0:
                continue
            # add lesson to graph with the same neigbours as subject
            graph.add_node(lesson, weight=len(subject.students))
            labels[lesson] = f'{subject.get_name()} ({lesson.length})'
            for neighbour in graph[subject]:
                graph.add_edge(lesson, neighbour)
        # lessons of the same subject are obviously connected
        for pair in combinations(subject.lessons, 2):
            graph.add_edge(*pair)
        # subject is no longer needed
        graph.remove_node(subject)
             
    return graph, labels, feasible_blocks

def generate_block_graph(db: Data):
    graph = Graph()
    # blocks taking place in different days can't possibly colide
    for day in range(5):
        blocks = db.session.query(LessonBlockDB).filter_by(day=day)
        graph.add_nodes_from(blocks)
        
        for b1, b2 in combinations(blocks, 2):
            # if one block starts after the second has ended...
            if b1.start+b1.length < b2.start \
            or b2.start+b2.length < b1.start:
                # ...the blocks don't collide
                continue
            graph.add_edge(b1, b2)
    return graph



