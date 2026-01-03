from .graphs import *
from data import Data, LessonBlockDB, Lesson
from queue import PriorityQueue
from itertools import count
from random import choice
from matplotlib import pyplot as plt

# def first_feasible(lesson: Lesson, feas, days, adj_colors):
    
#     return None


# def set_block(lesson: Lesson, block:LessonBlockDB, les_g, bl_g, adj_colors, colors, days):
#     colors[lesson] = block
#     if not block:
#         return False
#     for neighbour in les_g[lesson]:
#         adj_colors[neighbour].add(block)
#         adj_colors[neighbour].update(bl_g[block])
#     days[lesson.subject].append(block.day)
#     return True

def dfeas(les_g, bl_g, feas) -> dict[Lesson, LessonBlockDB]:
    
            
    # initialize data structures
    colors = {}
    days = {}
    adj_colors = {}
    uncolored = set()
    queue = PriorityQueue()

    counter = count()
    for lesson in les_g:
        days[lesson.subject] = []
        adj_colors[lesson] = set()
        # first lessons with fewer feasible blocks
        # if tied, longer lessons go first
        queue.put((len(feas[lesson]), -lesson.length, next(counter), lesson))


    # greedily color the graph
    while queue.qsize():
        lesson = queue.get()[-1]

        # get first feasible block
        first_feasible = None
        for block in feas[lesson]:
            if block.day in days[lesson.subject]:
                continue
            if block in adj_colors[lesson]:
                continue
            first_feasible = block 
            break 
        colors[lesson] = first_feasible

        if block:
            for neighbour in les_g[lesson]:
                adj_colors[neighbour].add(block)
                adj_colors[neighbour].update(bl_g[block])
            days[lesson.subject].append(block.day)


    return colors


def mutate(les_g, bl_g, feas, coloring: dict) -> tuple[dict, int]:
    child = coloring.copy()
    # find random uncolored lesson
    uncolored = [les for les, blo in child.items() if blo is None]
    if not len(uncolored):  
        return coloring, 0
    lesson = uncolored.pop()


    # force it randomly into solution
    block = choice(feas[lesson])
    child[lesson] = block
    # uncolor all nodes unhappy about it
    for neighbour in les_g[lesson]:
        n_block = child[neighbour]
        if n_block == block or n_block in bl_g[block]:
            child[neighbour] = None
            uncolored.append(neighbour)
    for other_lesson in lesson.subject.lessons:
        if other_lesson == lesson:
            continue
        if other_lesson in child:
            child[other_lesson] = None
            uncolored.append(other_lesson)
        # if other_lesson not in
        
    # try to fit uncolored lessons in
    queue = []
    # print(len(uncolored))
    # uncolored = {les for les, blo in child.items() if blo is None}
    # print(len(uncolored)) 
    for lesson in uncolored:
        queue.append((lesson, len(feas[lesson])))
    queue.sort(key=lambda x: x[1])
    # print(len(queue))
    for lesson, _ in queue:
        # if lesson.block_locked:
            # print('dupa')
        adj_cols = []
        for neighbour in les_g[lesson]:
            n_block = child[neighbour]
            if not n_block:
                continue
            adj_cols.append(n_block)
            adj_cols.extend(bl_g[n_block])
        
        m_days = []
        for other_lesson in lesson.subject.lessons:
            if other_lesson in child:
                block = child[other_lesson]
            else:
                block = other_lesson.block
            if block:
                m_days.append(block.day)
        # f = [bl for bl in feas[lesson] if not (bl in adj_cols or bl.day in m_days)]
        # if len(f):
        #     child[lesson] = f
        for block in feas[lesson]:
            if block in adj_cols:
                continue
            # print(block.day, m_days)
            if block.day in m_days:
                continue
            child[lesson] = block
            break

    # calculate score
    score = sum([len(les.subject.students) for les in uncolored])
    return child, score



def solve(db: Data, verbose=False):
    # create graphs
    les_g, labels, feas = generate_lesson_graph(db)
    bl_g = generate_block_graph(db)

    # generate initial coloring
    coloring = dfeas(les_g, bl_g, feas)
    if not len(coloring):
        return coloring
    
    # genetic loop
    pop_size = 200
    generations = 10
    cutoff = 25
    num_of_children = int(pop_size/cutoff) - 1

    cost = sum([len(les.subject.students) for les, block in coloring.items() if block is None])
    population = [(coloring, cost)]
    for _ in range(1,pop_size):
        population.append(mutate(les_g, bl_g, feas, coloring))
    population.sort(key= lambda x: x[1])
    best_scores = [cost]
    if verbose:
        print('Generation 0')
        print(f'Best score: {population[0][1]}')
        print(f'Cutoff score: {population[cutoff][1]}')
        print()
    for i in range(generations):
        new_pop = []
        for col in population[:cutoff]:
            new_pop.append(col)
            for _ in range(num_of_children):
                new_pop.append(mutate(les_g, bl_g, feas, col[0]))
        new_pop.sort(key=lambda x: x[1])
        population = new_pop
        best_scores.append(population[0][1])
        if verbose:
            print(f'Generation {i+1}')
            print(f'Best score: {population[0][1]}')
            print(f'Cutoff score: {population[cutoff][1]}')
            print()

    if verbose:
        plt.plot(best_scores)
        plt.show()
    coloring = population[0][0]

    return coloring

