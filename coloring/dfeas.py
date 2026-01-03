from .graphs import *
from data import Data, LessonBlockDB, Lesson
from queue import PriorityQueue
from itertools import count

def dfeas(les_g, bl_g, feas, colors={}) -> dict[Lesson, LessonBlockDB]:
    def first_feasible(lesson: Lesson):
        for block in feas[lesson]:
            if block.day in days[lesson.subject]:
                continue
            if block not in adj_colors[lesson]:
                return block
        return None
    
    def set_block(lesson: Lesson, block:LessonBlockDB):
        colors[lesson] = block
        if not block:
            return False
        for neighbour in les_g[lesson]:
            adj_colors[neighbour].add(block)
            adj_colors[neighbour].update(bl_g[block])
        days[lesson.subject].append(block.day)
        return True
        
    # initialize data structures
    days = {}
    adj_colors = {}
    uncolored = set()
    queue = PriorityQueue()

    counter = count()
    for lesson in les_g:
        days[lesson.subject] = []
        adj_colors[lesson] = set()
        if lesson in colors:
            continue

        # first lessons with fewer feasible blocks
        # if tied, longer lessons go first
        queue.put((len(feas[lesson]), -lesson.length, next(counter), lesson))

    # populate data structures
    for lesson, block in colors.items():
        set_block(lesson, block)

    # greedily color the graph
    while len(colors) < len(les_g):
        lesson = queue.get()[-1]
        if lesson in colors:
            continue
        block = first_feasible(lesson)
        set_block(lesson, block)

    return colors


def solve(db: Data):
    def fill_leftover(coloring: dict) -> dict:
        for lesson in les_g:
            if lesson in coloring.keys():
                continue
        pass

    # create graphs
    les_g, labels, feas = generate_lesson_graph(db)
    bl_g = generate_block_graph(db)

    colors = {}
    for block in db.all_lesson_blocks():
        for lesson in block.lessons:
            if lesson.block_locked:
                colors[lesson] = block

    # generate initial coloring
    coloring = dfeas(les_g, bl_g, feas, colors)
    return coloring
    # fill leftover lessons
    
    # genetic loop

