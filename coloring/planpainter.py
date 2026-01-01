import gcol
import itertools
from queue import PriorityQueue
from data import Data, Lesson, LessonBlockDB, Subject
from networkx import Graph, draw_networkx
import matplotlib.pylab as plt
import random
from gcol.node_coloring import _getNodeWeights, _check_params


def _partialcol(G, palette, color_of, W, it_limit, verbose, db: Data):
    k = len(palette)
    def domovepartialcol(v, j):
        # Used by partialcol to move node v to color j and update relevant
        # data structures
        block = palette[j]
        if block.length*5 != v.length or not db.is_teacher_available(v.subject.teacher, block):
            return
        color_of[v] = j
        db.add_lesson_to_block(v, palette[j])
        U.remove(v)
        for u in G[v]:
            Cost[u, j] += W[v]
            if color_of[u] == j or not is_feasible(u, u.block, db): ## not feasible
                Tabu[u, j] = its + t
                U.add(u)
                color_of[u] = -1
                db.remove_lesson_from_block(u)
                for w in G[u]:
                    Cost[w, j] -= W[u]

    # Use the current solution c to populate the data structures. C[v,j] gives
    # the total weight of the neighbors of v in color j, T is the tabu list,
    # and U is the set of clashing nodes
    assert k >= 1, "Error, partialcol only works with at least k = 1 color"
    Cost, Tabu, U, its = {}, {}, set(), 0
    for vertex in G:
        assert (
            isinstance(color_of[vertex], int) and color_of[vertex] >= -1 and color_of[vertex] < k
        ), ("Error, the coloring defined by c must allocate each node a ",
            "value from the set {-1,0,...,k-1}, where -1 signifies that ",
            "a node is uncolored")
        for color_j in range(k):
            Cost[vertex, color_j] = 0
            Tabu[vertex, color_j] = 0
    for vertex in G:
        if color_of[vertex] == -1:
            U.add(vertex)
        for neighbour in G[vertex]:
            if color_of[neighbour] != -1:
                Cost[vertex, color_of[neighbour]] += W[neighbour]
    currentcost = sum(W[u] for u in U)
    bestcost, bestsol, t = float("inf"), {}, 1
    if verbose > 0:
        print("    Running PartialCol algorithm using", k, "colors")
    while True:
        # Keep track of best solution and halt when appropriate
        if currentcost < bestcost:
            if verbose > 0:
                print("        Solution with", k, "colors and cost",
                    currentcost, "found by PartialCol at iteration", its)
            bestcost = currentcost
            bestsol = dict(color_of)
        if bestcost <= 0 or its >= it_limit:
            break
        # Evaluate all neighbors of current solution c
        its += 1
        vbest, jbest, bestval, numbestval = -1, -1, float("inf"), 0
        for vertex in U:
            for color_j in range(k):
                neighborcost = currentcost + Cost[vertex, color_j] - W[vertex]
                if neighborcost <= bestval:
                    if neighborcost < bestval:
                        numbestval = 0
                    # Consider the move if it is not tabu or leads to a new
                    # best solution
                    if Tabu[vertex, color_j] < its or neighborcost < bestcost:
                        if random.randint(0, numbestval) == 0:
                            vbest, jbest, bestval = vertex, color_j, neighborcost
                        numbestval += 1
        # Do the chosen move. If no move was chosen (all moves are tabu),
        # choose a random move
        if vbest == -1:
            vbest = random.choice(tuple(U))
            jbest = random.randint(0, k - 1)
            bestval = currentcost + Cost[vbest, jbest] - W[vbest]
        # Apply the move, update T, and determine the next tabu tenure t
        domovepartialcol(vbest, jbest)
        currentcost = bestval
        t = int(0.6 * len(U)) + random.randint(0, 9)
    if verbose > 0:
        print("    Ending PartialCol")
    return bestcost, bestsol, its


def is_feasible(lesson: Lesson, block: LessonBlockDB, db: Data):
    if not block:
        return True
    # print('kolicje: ' ,db.get_collisions_for_students_at_block(lesson.subject.students, block))
    # print(f'checking {}')
    print(block.length*5, lesson.length)
    if block.length*5 != lesson.length:
        return False # wrong block length
    if not (lesson.subject.parent() == block.parent() or lesson.subject.parent().get_class() == block.my_class):
        return False # wrong class
    # elif lesson.subject.teacher:
    #     print(f'{lesson.subject.teacher.name} is available at {block.print_full_time()}')
    # else:
    #     print('no teacher')
    if not db.is_teacher_available(lesson.subject.teacher, block):
        return False # teacher doesn't work at that time
    if len(db.get_collisions_for_students_at_block(lesson.subject.students, block)):
        return False # students are busy
    if len(db.get_collisions_for_teacher_at_block(lesson.subject.teacher, block)):
        return False # teacher is busy
    return True

def _dsatur(Graph, db: Data, colored=None, palette=None):

    # Dsatur algorithm for graph coloring. First initialise the data
    # structures. These are: the colors of each node c[v]; the degree d[v] of
    # each uncolored node in the graph induced by uncolored nodes; the set of
    # colors adjacent to each uncolored node (initially empty sets); and a
    # priority queue q. In q, each element has 4 values for the node v. The
    # first two are the the saturation degree of v, d[v] (as a tie breaker).
    # The third value is a counter, which just stops comparisons being made
    # with the final values, which might be of different types.
    d, adjcols, q = {}, {}, PriorityQueue()
    counter = itertools.count()
    for uncolored_node in Graph.nodes:
        d[uncolored_node] = Graph.degree(uncolored_node)
        adjcols[uncolored_node] = set()
        q.put((0, d[uncolored_node] * (-1), next(counter), uncolored_node))
    # If any nodes are already colored in c, update the data structures
    # accordingly
    if colored is not None:
        if not isinstance(colored, dict):
            raise TypeError(
                "Error, c should be a dict that assigns a subset of nodes ",
                "to colors"
            )
        for uncolored_node in colored:
            for v in Graph[uncolored_node]:
                if v not in colored:
                    adjcols[v].add(colored[uncolored_node])
                    d[v] -= 1
                    q.put((len(adjcols[v]) * (-1), d[v]
                        * (-1), next(counter), v))
                elif colored[uncolored_node] == colored[v]:
                    raise ValueError(
                        "Error, clashing nodes defined in supplied coloring"
                    )
    else:
        colored = {}
        # Color all remaining nodes
    while len(colored) < len(Graph):
        # Get the uncolored node u with max saturation degree, breaking ties
        # using the highest value for d. Remove u from q.
        _, _, _, uncolored_node = q.get()
        if uncolored_node not in colored:
            # Get lowest color label i for uncolored node u
            for i in itertools.count():
                if len(palette)<=i:
                    db.remove_lesson_from_block(uncolored_node)
                    i = -1
                    break
                if i not in adjcols[uncolored_node] and is_feasible(lesson=uncolored_node, block = palette[i], db=db):
                    db.add_lesson_to_block(uncolored_node, palette[i])
                    break
            colored[uncolored_node] = i 
            """ TODO set color"""
            # Update the data structures
            for v in Graph[uncolored_node]:
                if v not in colored:
                    adjcols[v].add(i)
                    d[v] -= 1
                    q.put((len(adjcols[v]) * (-1), d[v]
                        * (-1), next(counter), v))
    return colored
    
def min_cost_k_coloring(G, palette, db, weight=None, it_limit=40, verbose=0):
    
    k = len(palette)
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")

    # _check_params(G, "dsatur", 3, it_limit, verbose)
    if len(G) == 0:
        return {}
    c = _dsatur(G, db, {}, palette=palette)
    # print("Initial coloring")
    # for lesson, block_i in c.items():
    #     print(f'{lesson.subject.get_name()}: {block_i} {palette[block_i].print_full_time()}')
    # print(c)
    # return c
    W = {les: len(les.subject.students)for les in G} #_getNodeWeights(G, weight)
    # print(W)
    for v in c:
        if c[v] >= k:
            c[v] = -1
    cost, c, its = _partialcol(G, palette, c, W, it_limit, True, db)
    # print(_partialcol(G, palette, c, W, it_limit, verbose, db))
    # print("After PartialCol")
    # for lesson, block_i in c.items():
    #     print(f'{lesson.subject.get_name()}:{block_i} {palette[block_i].print_full_time()}')
    
    return c

def do_the_magic(db: Data):
    palette = db.all_lesson_blocks()
    graph, lables = generate_lesson_graph(db)
    c = min_cost_k_coloring(graph, palette, db)
    db.clear_all_lesson_blocks()
    for lesson, block_i in c.items():
        print(f'{lesson.subject.get_name()}: {block_i}{palette[block_i].print_full_time()}')
        if block_i == -1:
            db.remove_lesson_from_block(lesson)
        else:
            db.add_lesson_to_block(lesson, palette[block_i])
    return c


def generate_lesson_graph(db: Data):
    subject_graph = Graph()
    total_subjects = {}
    labels = {}
    for class_ in db.all_classes():
        total_subjects[class_] = []
        total_subjects[class_].extend(class_.subjects)
        for subclass in class_.subclasses:
            total_subjects[class_].extend(subclass.subjects)

        subject_graph.add_nodes_from(total_subjects[class_])
        # for subject in total_subjects[class_]:
            # labels[subject] = subject.get_name()
        for pair in itertools.combinations(total_subjects[class_], 2):
            # names = [s.get_name() for s in pair]
            # if subject_graph.has_edge(*pair):
                # continue
            for student in pair[0].students:
                if student in pair[1].students:
                    subject_graph.add_edge(*pair)
                    break
        
        for subject in total_subjects[class_]:
            for lesson in subject.lessons:
                subject_graph.add_node(lesson, weight=len(subject.students))
                labels[lesson] = f'{subject.get_name()} ({lesson.length})'
                for neighbour in subject_graph[subject]:
                    subject_graph.add_edge(lesson, neighbour)
            for pair in itertools.combinations(subject.lessons, 2):
                subject_graph.add_edge(*pair)
            subject_graph.remove_node(subject)


             
    # draw_networkx(subject_graph, labels=labels)
    # plt.show()
    return subject_graph, labels

    
        
    # for lesson in db.session.query(Lesson).all():
