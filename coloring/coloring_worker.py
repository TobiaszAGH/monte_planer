from .graphs import generate_block_graph, generate_lesson_graph
from .functions import crazy, mutate
from PyQt5.QtCore import QThread, pyqtSignal
from db_config import settings

class ColoringThread(QThread):
    next_generation = pyqtSignal(int, int)
    finished = pyqtSignal(dict, list, list)

    def __init__(self, db):
        super().__init__()
        self.db = db

    def run(self):
        # create graphs
        les_g, labels, feas = generate_lesson_graph(self.db)
        bl_g = generate_block_graph(self.db)

        
        # genetic loop
        pop_size = settings.pop_size
        generations = settings.generations
        cutoff = int(settings.cutoff*pop_size)
        num_of_children = int(pop_size/cutoff)
        population = []
        for _ in range(pop_size):

            coloring = crazy(les_g, bl_g, feas)
            cost = sum([len(les.subject.students) for les, block in coloring.items() if block is None])
            population.append((coloring, cost))
            
        # for _ in range(1,pop_size):
            # population.append(mutate(les_g, bl_g, feas, coloring))
        population.sort(key= lambda x: x[1])
        best_scores = [population[0][1]]
        cutoffs = [population[cutoff][1]]
        goat = (population[0])
        self.next_generation.emit(0, population[0][1])
        for i in range(generations):
            new_pop = []
            for col in population[:cutoff]:
                # new_pop.append(col)
                for _ in range(num_of_children):
                    new_pop.append(mutate(les_g, bl_g, feas, col[0]))
            new_pop.sort(key=lambda x: x[1])
            population = new_pop
            bs = population[0][1]
            if bs < goat[1]:
                goat = population[0]
            best_scores.append(bs)
            cutoffs.append(population[cutoff][1])
            self.next_generation.emit(i+1, population[0][1])

        
        coloring = goat[0]

        self.finished.emit(coloring, best_scores, cutoffs)

