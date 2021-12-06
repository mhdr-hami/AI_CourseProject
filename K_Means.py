import random
import math
import sys
from tools import *
from State import *


def InitializeMeans(points, k):
    means = []
    while len(means) != k:
        mean = random.choice(points)
        if mean not in means:
            means.append(mean)

    return means


def EuclideanDistance(point1: tuple, point2: tuple):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def UpdateMeans(clusters):
    means = []
    for cluster in clusters:
        Sum_X = 0
        Sum_Y = 0
        for point in cluster:
            Sum_X += point[0]
            Sum_Y += point[1]
        Sum_X /= len(cluster)
        Sum_Y /= len(cluster)
        means.append((Sum_X, Sum_Y))
    return means


def isEqual(means1, means2):
    for mean in range(len(means1)):
        if means1[mean] != means2[mean]:
            return False
    return True


def Classify_Clusters(points, means):
    clusters = [[] for i in range(len(means))]
    for point in points:
        minimum = + sys.maxsize
        index = None

        for mean in range(len(means)):
            dist = EuclideanDistance(point, means[mean])
            if dist <= minimum:
                minimum = dist
                index = mean

        clusters[index].append(point)
    return clusters


def Calculate_K_means(k, points, bases, max_iterations=10000):
    # means = InitializeMeans(points, k)
    means = bases
    clusters = Classify_Clusters(points, means)
    # for e in range(max_iterations):
    #     means2 = UpdateMeans(clusters)
    #     if isEqual(means, means2):
    #         break
    #     means = means2
    clusters = Classify_Clusters(points, means)
    return clusters, means


def Clusters_Value(clusters, means, state: State, required_diamond, tools: SearchPath, MPV):
    print(state.stateDiamonds)
    taken_diamonds = [state.stateDiamonds[i] for i in range(0, len(state.stateDiamonds), 2)]
    print(taken_diamonds)
    value_clusters = []
    agent_coordinate = state.agents[0].position

    diamonds = state.allDiamonds
    bases = state.allBases

    for i in range(len(clusters)):
        cluster = clusters[i]
        sum_diamonds = 0
        Rule1 = 40
        Rule2 = 0
        Rule3 = 0
        cluster_diamonds = []

        # RULE 1
        # Minimum Required Diamonds
        total_diamond = [0, 0, 0, 0, 0]
        coEfficients = [0, 0, 0, 0, 0]

        for d in taken_diamonds:
            total_diamond[int(d[0])] += 1
        for d in cluster_diamonds:
            total_diamond[int(d[0])] += 1
        for r_d in range(len(required_diamond)):
            if required_diamond[r_d] <= total_diamond[r_d]:
                coEfficients[r_d] = 1

        for j in range(len(cluster)):
            point = cluster[j]
            if j % 2 == 0:
                x = point[1][0]
                y = point[1][1]
                if isDiamond(tools.g.mapp[x][y]):
                    sum_diamonds += coEfficients[int(tools.g.mapp[x][y])] * value(tools.g.mapp[x][y])
                    cluster_diamonds.append(point)


        # RULE 2
        # if 5 continuous colors -> Win!
        # check if it's possible to apply rule 2 and win the game
        total_taken_diamonds = taken_diamonds
        for diamond in cluster_diamonds:
            total_taken_diamonds.append(diamond[0])

        if distinctContinuousColors(total_taken_diamonds) == 5:
            Rule2 = 10000

        # RULE 3
        # yellow-green-yellow
        # not yellow && not green
        remainingDiamondsColors = [diamonds[i][0] for j in range(len(diamonds))]
        if len(taken_diamonds) >= 1 and taken_diamonds[-1] != "3" and taken_diamonds[-1] != "0":
            if "3" in remainingDiamondsColors:
                Rule3 = 40
        # last one is Yellow
        if len(taken_diamonds) >= 1 and taken_diamonds[-1] == "3":
            if "0" in remainingDiamondsColors:
                Rule3 = 100
        if len(taken_diamonds) >= 2 and taken_diamonds[-1] == "0" and taken_diamonds[-2] == "3":
            if "3" in remainingDiamondsColors:
                Rule3 = 300

        cluster_val = ((Rule1 * sum_diamonds + Rule2 + Rule3) / (MPV * 40 + 300 + 10000)) * 15
        value_clusters.append(cluster_val)

    # list of clusters values
    return value_clusters