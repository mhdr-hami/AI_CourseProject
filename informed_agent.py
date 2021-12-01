import random
import heapq
import sys
import math
import functools
from base import BaseAgent, TurnData, Action


@functools.total_ordering
class Node:
    def __init__(self, content, coordinate):
        self.content = content
        self.coordinate = coordinate
        self.parent = (-1, -1)
        self.f = sys.maxsize
        self.g = sys.maxsize
        self.h = sys.maxsize
        self.action = None
        self.visited = False

    def __gt__(self, other):
        return self.f > other.f

    def __eq__(self, other):
        return self.f == other.f


class InformedSearch:
    def __init__(self, mp):
        self.graph = [[Node(mp[i][j], (i, j)) for j in range(len(mp[0]))] for i in range(len(mp))]
        self.queue = []

    def isInTable (self, point: tuple):
        x = point[0]
        y = point[1]
        if (x >= 0) and (x < len(self.graph)) and (y >= 0) and (y < len(self.graph[0])):
            return True
        return False

    def findChildren(self, point: tuple):
        x = point[0]
        y = point[1]
        children = []
        if self.isInTable((x, y-1)):
            if self.graph[x][y-1].content != "*":
                children.append((x, y-1))
        if self.isInTable((x, y+1)):
            if self.graph[x][y + 1].content != "*":
                children.append((x, y+1))
        if self.isInTable((x-1, y)):
            if self.graph[x-1][y].content != "*":
                children.append((x-1, y))
        if self.isInTable((x+1, y)):
            if self.graph[x+1][y].content != "*":
                children.append((x+1, y))
        return children

    def solutionPath(self, goal: tuple):
        x = goal[0]
        y = goal[1]
        solution = []
        while not ((self.graph[x][y].parent[0] == x) and (self.graph[x][y].parent[1] == y)):
            solution.insert(0, self.graph[x][y].action)
            temp_x = self.graph[x][y].parent[0]
            temp_y = self.graph[x][y].parent[1]
            x = temp_x
            y = temp_y
        return solution

    def takeAction(self, pre: tuple, current: tuple):
        if pre[0] - 1 == current[0]:
            return "UP"
        if pre[0] + 1 == current[0]:
            return "DOWN"
        if pre[1] - 1 == current[1]:
            return "LEFT"
        if pre[1] + 1 == current[1]:
            return "RIGHT"

    @staticmethod
    def heuristicCalculation(current: tuple, goal: tuple):
        return math.sqrt((current[0] - goal[0])**2 + (current[1] - goal[1])**2)

    def A_star_Search(self, start: tuple, goal: tuple):
        xstart = start[0]
        ystart = start[1]
        self.graph[xstart][ystart].f = 0
        self.graph[xstart][ystart].g = 0
        self.graph[xstart][ystart].h = 0
        self.graph[xstart][ystart].parent = (xstart, ystart)

        heapq.heappush(self.queue, (self.graph[xstart][ystart].f, self.graph[xstart][ystart]))

        while self.queue:
            temp_top = heapq.heappop(self.queue)
            top = temp_top[1]
            self.graph[top.coordinate[0]][top.coordinate[1]].visited = True
            children = self.findChildren(top.coordinate)
            for child in children:
                G = top.g + 1
                H = self.heuristicCalculation(child, goal)
                F = G + H

                if not self.graph[child[0]][child[1]].visited:
                    temp_f = self.graph[child[0]][child[1]].f

                    if temp_f > F and temp_f != sys.maxsize:
                        self.graph[child[0]][child[1]].parent = top.coordinate
                        self.graph[child[0]][child[1]].action = self.takeAction(top.coordinate, child)
                        self.graph[child[0]][child[1]].g = G
                        self.graph[child[0]][child[1]].h = H
                        self.graph[child[0]][child[1]].f = F
                        heapq.heapreplace(self.queue, (F, self.graph[child[0]][child[1]]))

                    elif temp_f == sys.maxsize:
                        self.graph[child[0]][child[1]].parent = top.coordinate
                        self.graph[child[0]][child[1]].action = self.takeAction(top.coordinate, child)
                        self.graph[child[0]][child[1]].g = G
                        self.graph[child[0]][child[1]].h = H
                        self.graph[child[0]][child[1]].f = F
                        heapq.heappush(self.queue, (F, self.graph[child[0]][child[1]]))

                    if child[0] == goal[0] and child[1] == goal[1]:
                        return self.solutionPath(goal)

    def Dijkstra_Backwards(self, start: tuple):
        self.queue = []
        for i in range(len(self.graph)):
            for j in range(len(self.graph[0])):
                self.graph[i][j].parent = (-1, -1)
                self.graph[i][j].action = None
                self.graph[i][j].g = sys.maxsize
                self.graph[i][j].h = 0
                self.graph[i][j].f = sys.maxsize
                self.graph[i][j].visited = False

        xstart = start[0]
        ystart = start[1]
        self.graph[xstart][ystart].f = 0
        self.graph[xstart][ystart].g = 0
        self.graph[xstart][ystart].h = 0
        self.graph[xstart][ystart].parent = (xstart, ystart)

        heapq.heappush(self.queue, (self.graph[xstart][ystart].f, self.graph[xstart][ystart]))

        while self.queue:
            temp_top = heapq.heappop(self.queue)
            top = temp_top[1]
            self.graph[top.coordinate[0]][top.coordinate[1]].visited = True
            children = self.findChildren(top.coordinate)
            for child in children:
                G = top.g + 1
                H = 0
                F = G + H

                if not self.graph[child[0]][child[1]].visited:
                    temp_f = self.graph[child[0]][child[1]].f

                    if temp_f > F and temp_f != sys.maxsize:
                        self.graph[child[0]][child[1]].parent = top.coordinate
                        self.graph[child[0]][child[1]].action = self.takeAction(top.coordinate, child)
                        self.graph[child[0]][child[1]].g = G
                        self.graph[child[0]][child[1]].h = H
                        self.graph[child[0]][child[1]].f = F
                        heapq.heapreplace(self.queue, (F, self.graph[child[0]][child[1]]))

                    elif temp_f == sys.maxsize:
                        self.graph[child[0]][child[1]].parent = top.coordinate
                        self.graph[child[0]][child[1]].action = self.takeAction(top.coordinate, child)
                        self.graph[child[0]][child[1]].g = G
                        self.graph[child[0]][child[1]].h = H
                        self.graph[child[0]][child[1]].f = F
                        heapq.heappush(self.queue, (F, self.graph[child[0]][child[1]]))

                    if self.graph[child[0]][child[1]].content == "a":
                        return self.solutionPath((child[0], child[1]))

def go(act: str):
    if act == "DOWN":
        return Action.DOWN
    if act == "UP":
        return Action.UP
    if act == "RIGHT":
        return Action.RIGHT
    if act == "LEFT":
        return Action.LEFT


def find_diamonds_bases(bmap):
    diamonds = []
    bases = []
    for r in range(len(bmap)):
        for c in range(len(bmap[r])):
            if bmap[r][c] == '1':
                diamonds.append((r, c))
            if bmap[r][c] == "a":
                bases.append(r * len(bmap) + c)

    return diamonds, bases


class Agent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.solution = []
        self.diamonds_cors = []
        self.base_cors = []
        self.algo = None
        self.state = 0

    def do_turn(self, turn_data: TurnData) -> Action:
        if self.state == 0:
            agent_coordinate = turn_data.agent_data[0].position
            self.diamonds_cors, self.base_cors = find_diamonds_bases(turn_data.map)
            self.algo = InformedSearch(turn_data.map)
            self.solution = self.algo.A_star_Search(agent_coordinate, self.diamonds_cors[0])
            act = self.solution.pop(0)
            if not self.solution:
                self.state = 2
            else:
                self.state = 1
            return go(act)

        if self.state == 1:
            if self.solution:
                if len(self.solution) == 1:
                    self.state = 2
                act = self.solution.pop(0)
                return go(act)

        if self.state == 2:
            self.solution = self.algo.Dijkstra_Backwards(turn_data.agent_data[0].position)
            act = self.solution.pop(0)
            self.state = 3
            return go(act)

        if self.state == 3:
            if self.solution:
                if len(self.solution) == 1:
                    self.state = 1
                act = self.solution.pop(0)
                return go(act)


if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)