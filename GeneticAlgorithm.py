import random
from itertools import product

import ga
import math
from tools import *
import numpy as np
from base import BaseAgent, TurnData, Action


class Agent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.solution = []
        self.state = 0
        self.diamond_permutation = []
        self.tools = None

    def do_turn(self, turn_data: TurnData) -> Action:
        if self.state == 0:

            mp = turn_data.map
            graph = Graph(len(mp), len(mp[0]), mp)
            graph.fillChilds()
            self.tools = SearchPath(graph)
            #  genetic algorithm parameters
            diamonds = ga.find_diamonds(turn_data.map)  # color and coordinate

            #  check if there is only one diamond, return the solution now!
            if len(diamonds) == 1:
                self.solution = self.tools.OLDBFS(turn_data.agent_data[0].position, diamonds[0][1])
                self.state = 1
                self.diamond_permutation = diamonds
                act = self.solution.pop(0)
                return act

            bases = find_bases_tuple(turn_data.map)
            num_parents_mating = 16  # ?
            population_size = 0
            fitness_dict = dict()
            population_size = (2*len(diamonds)**3, 2*len(diamonds))
            # if len(diamonds) > 4:
            #     population_size = (int(math.factorial(len(diamonds))/5), 2 * len(diamonds))  # ?
            # else:
            #     population_size = (int(math.factorial(len(diamonds))), 2 * len(diamonds))  # ?

            num_generations = 10*len(diamonds) + 20  # ?
            pc = 0.9
            pm = 0.1

            #  Defining population
            new_population = []
            for _ in range(population_size[0]):
                diamonds_perm = np.random.permutation(len(diamonds))
                bases_perm = list(product([i for i in range(len(bases))], repeat=len(diamonds)))
                baseIndex = np.random.randint(0, len(bases_perm))
                diamondsList = [diamonds[i] for i in diamonds_perm]
                basesList = [bases[i] for i in bases_perm[baseIndex]]
                chromosome = joinLists(diamondsList, basesList)
                new_population.append(chromosome)
            #  Generations will be born and dead...
            for generation in range(num_generations):
                # print("Generation :", generation, sep=" ")

                # measuring the fitness for each chromosome in population
                fitness, new_population = ga.calculate_fitness(turn_data.turns_left, new_population, self.tools,
                                                               turn_data.agent_data[0].position, fitness_dict)
                # print("Fitness :", fitness, new_population, sep=" ")

                # selection best parents for mating
                parents = ga.parents_selection(num_parents_mating, fitness, new_population)
                # print("Parents :", parents, sep=" ")

                # generating the next generation
                offspring_crossover = ga.crossover(parents, pc)  # ? offspring_size
                # print("Crossover :", offspring_crossover, sep=" ")

                offspring_mutation = ga.mutation(offspring_crossover, pm)
                # print("Mutation :", offspring_crossover, sep=" ")

                new_population += offspring_mutation

            # finding best chromosome as the solution
            fitness, new_population = ga.calculate_fitness(turn_data.turns_left, new_population, self.tools,
                                                           turn_data.agent_data[0].position, fitness_dict)
            new_population = new_population[:population_size[0]]

            self.diamond_permutation = new_population[0]
            print(self.diamond_permutation)

            # find the path to the first diamond ( then iterate over gens, append to solution)
            self.solution += self.tools.BFS(turn_data.agent_data[0].position, self.diamond_permutation[0][1])
            self.solution += self.tools.BFS_NoWall(self.diamond_permutation[0][1], self.diamond_permutation[1])

            print(self.solution)

            #  moving towards the diamonds
            self.state = 1

            if len(self.solution):
                act = self.solution.pop(0)
            else:
                while 1:
                    return Action.UP
            return act

        if self.state == 1:
            # we have a solution and we will use it until it's empty
            if self.solution:
                if len(self.solution) == 1:
                    self.state = 1
                    last_diamond = self.diamond_permutation.pop(0)
                    if len(self.diamond_permutation):
                        self.diamond_permutation.pop(0)
                    self.tools.g.fillXY(last_diamond[1][0], last_diamond[1][1], '.')
                    self.state = 2
                if len(self.solution):
                    act = self.solution.pop(0)
                else:
                    while 1:
                        return Action.UP
                return act

        if self.state == 2:
            self.solution += self.tools.BFS(turn_data.agent_data[0].position, self.diamond_permutation[0][1])
            self.solution += self.tools.BFS_NoWall(self.diamond_permutation[0][1], self.diamond_permutation[1])

            print(self.solution)

            #  moving towards the diamonds
            self.state = 1
            if len(self.solution):
                act = self.solution.pop(0)
            else:
                while 1:
                    return Action.UP

            return act


if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)
