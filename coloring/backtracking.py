import matplotlib.pylab as plt
from networkx import Graph, draw_networkx
from data import Data, LessonBlockDB, Lesson, Class
from itertools import combinations, count
from queue import PriorityQueue
from typing import List


def generate_lesson_graph(db: Data):
    graph = Graph()
    total_subjects = {}
    labels = {}
    for class_ in db.all_classes():
        total_subjects[class_] = []
        total_subjects[class_].extend(class_.subjects)
        for subclass in class_.subclasses:
            total_subjects[class_].extend(subclass.subjects)

        graph.add_nodes_from(total_subjects[class_])
        for pair in combinations(total_subjects[class_], 2):
            if pair[0].teacher == pair[1].teacher and pair[0].teacher is not None:
                graph.add_edge(*pair)
                continue
            for student in pair[0].students:
                if student in pair[1].students:
                    graph.add_edge(*pair)
                    break
        
        for subject in total_subjects[class_]:
            for lesson in subject.lessons:
                graph.add_node(lesson, weight=len(subject.students))
                labels[lesson] = f'{subject.get_name()} ({lesson.length})'
                for neighbour in graph[subject]:
                    graph.add_edge(lesson, neighbour)
            for pair in combinations(subject.lessons, 2):
                graph.add_edge(*pair)
            graph.remove_node(subject)

             
    return graph, labels

def generate_block_graph(db: Data):
    graph = Graph()
    for day in range(5):
        blocks = db.session.query(LessonBlockDB).filter_by(day=day)
        blocks = db.all_lesson_blocks()
        for block in blocks:
            graph.add_node(block)
        
        for b1, b2 in combinations(blocks, 2):
            if b1.start+b1.length < b2.start \
            or b2.start+b2.length < b1.start:
                continue
            graph.add_edge(b1, b2)
    return graph



def backtracking(lesson_graph: Graph, block_graph: Graph, colors: dict, db: Data):
    def calc_cost(les_g, colors):
        return sum([
            len(les.subject.students) 
            for les in les_g 
            if les not in colors.keys() # not yet checked
            or colors[les] is None # set as uncolored
        ])
    
    def min_cost(colors):
        return sum({
            len(les.subject.students)
            for les, block in colors.items()
            if block is None
        })
    
    # remove 
    def dynamic_feas(les: LessonBlockDB):
        df = [
            bl for bl in feasible_blocks[les]
            if bl not in adj_colors[les]
        ]
        df.append(None)
        return df
    
    # finds the lesson with the fewer number of feasible blocks
    def next_lesson(queue: dict):
        low_pri = float('inf')
        next_les = None
        for item, priority in queue.items():
            if priority >= low_pri:
                continue
            low_pri = priority
            next_les = item
        if next_les:
            queue.pop(next_les)
        
        
        return next_les
    
    def util(les_g: Graph, bl_g, colors: dict, queue: PriorityQueue, les, solution):
        # reached the end
        if les is None:
            return True
        # this branch won't have any fruit
        if min_cost(colors) > solution['best_cost']:
            return
        # check every possible block (or leaving empty)
        for bl in dynamic_feas(les):
            colors[les] = bl
            # update data structures
            if bl is not None:
                for neighbour in les_g[les]:
                    if neighbour in colors.keys() or neighbour==les:
                        continue
                    adj_colors[neighbour].append(bl)
                    adj_colors[neighbour].extend(bl_g[bl])
                    n_df = dynamic_feas(neighbour)
                    queue[neighbour] = len(n_df)

                # calculate cost and add solution
                cost = calc_cost(les_g, colors)
                if cost == solution['best_cost']:
                    solution['colors'].append(colors.copy())

                if cost < solution['best_cost']:
                    solution['best_cost'] = cost
                    solution['colors'] = [colors.copy()]

            # checkout the lesson with the lowest number of feasible blocks 
            next_les = next_lesson(queue)
            util(les_g, bl_g, colors.copy(), queue.copy(), next_les, solution)

            # backtrack from this branch 
            colors.pop(les)
            for neighbour in les_g[les]:
                if neighbour in colors.keys() or bl is None:
                    continue
                adj_colors[neighbour].remove(bl)
                for n_bl in bl_g[bl]:
                    adj_colors[neighbour].remove(n_bl)
                n_df = dynamic_feas(neighbour)
                queue[neighbour] = len(n_df)


    adj_colors = {}
    feasible_blocks = {}
    queue = {}
    lesson: Lesson
    block: LessonBlockDB
    # generate static feasibility
    for lesson in lesson_graph.nodes:
        feasible_blocks[lesson] = []
        adj_colors[lesson] = []
        for block in block_graph.nodes:
            if block.length*5 != lesson.length: # wrong length
                continue
            if not db.is_teacher_available(lesson.subject.teacher, block): # teacher doesn't work at that time
                continue

            possible_sub_classes = [block.parent()]
            if isinstance(possible_sub_classes[0], Class):
                possible_sub_classes.extend(block.parent().subclasses)
            if lesson.subject.parent() not in possible_sub_classes:
                continue
            feasible_blocks[lesson].append(block)
        queue[lesson] = len(feasible_blocks[lesson])

    # load colors from dict and adjust dynamic feasibility
    for les, block in colors.items():
        queue.pop(les)
        for neighbour in lesson_graph[les]:
            if neighbour in colors.keys():
                continue
            adj_colors[neighbour].append(block)
            adj_colors[neighbour].extend(block_graph[block])
            df = dynamic_feas(neighbour)
            queue[neighbour] = len(df)

    solution = {
        'best_cost': float('inf'),
        'colors': []
    }

    # plant the tree
    les = next_lesson(queue)
    util(lesson_graph, block_graph, colors, queue, les, solution)

    return solution['best_cost'], solution['colors']


def find_exact_solutions(db: Data):
    les_g, labels = generate_lesson_graph(db)
    # draw_networkx(les_g, labels=labels)
    # plt.show()
    bl_g = generate_block_graph(db)
    colors = {}
    for block in db.session.query(LessonBlockDB).all():
        for lesson in block.lessons:
            if lesson.block_locked:
                colors[lesson] = block
    return backtracking(les_g, bl_g, colors, db)


    

    
    




    

