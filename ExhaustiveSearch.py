import random

import numpy

from base import BaseAgent, TurnData, Action
from itertools import permutations, product
from tools import *


class ExhaustiveSearch:
    def __init__(self, g: Graph):
        self.searchPath = SearchPath(g)

    def bestDiamondPermutation(self, start: tuple, turnsLeft: int, diamonds, bases):

        permsDiamonds = list(permutations([i for i in range(len(diamonds))]))

        permsBases = list(product([i for i in range(len(bases))], repeat=len(diamonds)))


        dPerm = [diamonds[i] for i in list(permsDiamonds[0])]
        bPerm = [bases[i] for i in list(permsBases[0])]
        ans = self.permutationValue(start, permsDiamonds[0], permsBases[0], turnsLeft, diamonds, bases), joinLists(dPerm, bPerm)

        for i in range(len(permsDiamonds)):
            for j in range(len(permsBases)):
                thisPermutationValue = self.permutationValue(start, permsDiamonds[i], permsBases[j], turnsLeft, diamonds, bases)
                if ans[0][0] < thisPermutationValue[0] or\
                        (ans[0] == thisPermutationValue[0] and ans[0][1] > thisPermutationValue[1]):
                    dlist = [diamonds[index] for index in permsDiamonds[i]]
                    blist = [bases[index] for index in permsBases[j]]
                    ans = thisPermutationValue, joinLists(dlist, blist)
        print("bestANS", ans)
        # ans is ((best possible value, cost of best possible value) , the permutation that made that Value)
        return ans[1]

    def permutationValue(self, start: tuple, permDiamond: list, permBase: list, turnsLeft: int, diamond, bases):
        dPerm = [diamond[i] for i in list(permDiamond)]
        bPerm = [bases[i] for i in list(permBase)]
        mergedPerm = joinLists(dPerm, bPerm)
        print(mergedPerm)
        cost = 0
        V = 0
        pos = start
        taken = []
        for i in range(len(mergedPerm)):
            if i % 2 == 0:
                dist = len(self.searchPath.BFS_Forward(pos, mergedPerm[i][1]))
                if dist == 0:
                    dist = float('inf')
                taken.append(i)
                self.searchPath.g.fillXY(mergedPerm[i][1][0], mergedPerm[i][1][1], '.')
                if cost + dist > turnsLeft:
                    break
                cost += dist
                pos = mergedPerm[i][1]
            else:
                dist = len(self.searchPath.BFS_Forward_No_Wall(pos, mergedPerm[i]))
                if dist == 0:
                    dist = float('inf')
                if cost + dist > turnsLeft:
                    break
                cost += dist
                pos = mergedPerm[i]
                V += value(mergedPerm[i - 1][0])

        for i in taken:
            self.searchPath.g.fillXY(mergedPerm[i][1][0], mergedPerm[i][1][1], mergedPerm[i][0])
        print(V, cost)
        print()
        return V, cost
