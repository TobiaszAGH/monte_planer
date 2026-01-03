import matplotlib.pylab as plt
from networkx import Graph, draw_networkx
from data import Data, LessonBlockDB, Lesson, Class
from itertools import combinations, count
from queue import PriorityQueue
from typing import List
from random import randint
from .graphs import generate_lesson_graph, generate_block_graph



def backtracking(lesson_graph: Graph, block_graph: Graph, colors: dict, db: Data, feasible_blocks):
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
    
    def util(les_g: Graph, bl_g, colors: dict, queue: PriorityQueue, les, solution, Tabu):
        if len(colors) == len(les_g.nodes): 
            return True
      
        for bl in dynamic_feas(les):
            # if Tabu[les, bl] > solution['its']:
                # continue
            colors[les] = bl
            # update data structures

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
                print(cost, len(colors), len(les_g.nodes), solution['its'])
                solution['colors'].append(colors.copy())

            if cost < solution['best_cost']:
                print(cost)
                solution['best_cost'] = cost
                solution['colors'] = [colors.copy()]

            # if cost > solution['best_cost']:

                # Tabu[les, bl] = solution['its'] + int(0.6 * (len(les_g.nodes) - len([v for v in colors if v]))) + randint(0,15)

            # checkout the lesson with the lowest number of feasible blocks 
            next_les = next_lesson(queue)
            if util(les_g, bl_g, colors.copy(), queue.copy(), next_les, solution, Tabu):
                return True

            # backtrack from this branch 
            colors.pop(les)
            queue[les] = len(dynamic_feas(les))
            for neighbour in les_g[les]:
                if neighbour in colors.keys() or bl is None:
                    continue
                adj_colors[neighbour].remove(bl)
                for n_bl in bl_g[bl]:
                    adj_colors[neighbour].remove(n_bl)
                n_df = dynamic_feas(neighbour)
                queue[neighbour] = len(n_df)
        return False

    counter = count()
    adj_colors = {}
    Tabu = {}
    queue = {}
    lesson: Lesson
    block: LessonBlockDB

    for les in lesson_graph:
        queue[les] = len(feasible_blocks[les])
        adj_colors[les] = []
    


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
        'best_cost': calc_cost(lesson_graph, colors),
        'colors': [colors.copy()],
        'its': 0
    }

    # plant the tree
    les = next_lesson(queue)
    print(util(lesson_graph, block_graph, colors, queue, les, solution, Tabu))
    print(solution)

    return solution['best_cost'], solution['colors']


def find_exact_solutions(db: Data):
    les_g, labels, feasable_blocks = generate_lesson_graph(db)
    draw_networkx(les_g, labels=labels)
    plt.show()
    bl_g = generate_block_graph(db)
    colors = {}
    for block in db.session.query(LessonBlockDB).all():
        for lesson in block.lessons:
            if lesson.block_locked:
                colors[lesson] = block
    return backtracking(les_g, bl_g, colors, db, feasable_blocks)


    

    
    




    

