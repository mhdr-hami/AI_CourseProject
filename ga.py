import numpy as np
import random
from tools import *
from base import BaseAgent, TurnData, Action


def disability_check(chromosome: list):
    for gene in range(len(chromosome)):
        if gene % 2 == 0 and chromosome.count(chromosome[gene]) > 1:
            return True
    return False


def calculate_fitness(turn_num, population: list, tools: SearchPath, agent_position, fitness_dict: dict):
    fitness = []

    for chromosome in population:
        if tuple(chromosome) in fitness_dict:
            fitness.append(fitness_dict[tuple(chromosome)])

        else:
            taken = []
            agent_pos = agent_position
            passed_turn = 0
            if disability_check(chromosome):
                population.remove(chromosome)

            else:
                fit_value = 0
                for i in range(len(chromosome)):
                    gene = chromosome[i]
                    if i % 2 == 0:
                        # diamond
                        dist = len(tools.BFS(agent_pos, gene[1]))
                        tools.g.fillXY(gene[1][0], gene[1][1], '.')
                        taken.append(i)
                        if dist == 0:
                            dist = float('inf')
                        else:
                            agent_pos = gene[1]
                    else:
                        #base
                        dist = len(tools.BFS_NoWall(agent_pos, gene))
                        if dist == 0:
                            dist = float('inf')
                        else:
                            agent_pos = gene

                    if dist + passed_turn <= turn_num:
                        passed_turn = passed_turn + dist
                        if i % 2 == 1:
                            fit_value = fit_value + value(chromosome[i - 1][0])
                    else:
                        break
                fitness.append(fit_value)
                fitness_dict[tuple(chromosome)] = fit_value

                for i in taken:
                    tools.g.fillXY(chromosome[i][1][0], chromosome[i][1][1], chromosome[i][0])

    fitness, population = zip(*sorted(zip(fitness, population), reverse=True))
    fitness = list(fitness)
    population = list(population)
    return fitness, population


def parents_selection(parents_num, fitness, population):
    pass
    # parents can be selected more than once ? if yes, how to mate them?

    # consider probability or not?
    # if not:
    parents = population[0:parents_num]
    return parents

    # if yes:
    # sum_fitness = 0
    # for i in fitness:
    #     sum_fitness = sum_fitness + i
    # prob_fitness = np.empty(len(fitness))
    # for i in range(0, len(prob_fitness)):
    #     prob_fitness[i] = fitness[i] / sum_fitness
    # parents = []
    # while len(parents) != parents_num:
    #     parent = random.choices(population, weights=prob_fitness, k=1)
    #     if parent not in parents:
    #         parents.append(parent[0])
    # return parents


def crossover(parents, p_c):
    offspring = []
    k = len(parents)
    l = len(parents[0])

    for i in range(0, k, 2):

        crossover_point = np.random.randint(1, l)  # ?

        offspring = offspring + list([(parents[i][0:crossover_point + 1] + parents[(i+1) % k][crossover_point + 1:l])])

        offspring = offspring + list([(parents[(i+1) % k][0:crossover_point + 1] + parents[i][crossover_point + 1:l])])

    return offspring


def mutation(offspring_crossover, p_m):
    for offspring in offspring_crossover:
        probability = np.random.uniform(0, 1)
        if probability <= p_m:
            r0 = np.random.randint(0, len(offspring))
            r1 = r0
            while r1 == r0 or (r0 % 2 != r1 % 2):
                r1 = np.random.randint(0, len(offspring))
            temp = offspring[r0]
            offspring[r0] = offspring[r1]
            offspring[r1] = temp
    # for offspring in offspring_crossover:
    #     for gene in range(0, len(offspring)):
    #         probability = np.random.uniform(0, 1)
    #         if probability <= p_m:
    #             rand_gene = random.choice(diamonds)
    #             offspring[gene] = rand_gene
    return offspring_crossover


