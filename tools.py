
from base import BaseAgent, TurnData, Action


class Node:
    def __init__(self, content, childs: list, coordinate: tuple, row):
        self.coordinate = coordinate
        self.content = content
        self.actionSrc = None
        self.actionGoal = None
        self.parentSrc = -1
        self.parentGoal = -1

        self.childs = childs
        self.index = row * coordinate[0] + coordinate[1]


class Graph:
    def __init__(self, rows, cols, mapp):
        self.index_based_dict = {}
        self.childs_list = []
        self.mapp = mapp
        self.rows = rows
        self.cols = cols

    def fillXY(self, x, y, val):
        self.index_based_dict[makeScallar(self.cols, x, y)].content = val
        self.mapp[x] = self.mapp[x][:y] + [str(val)] + self.mapp[x][y + 1:]

    def fillChilds(self):
        for r in range(self.rows):
            for c in range(self.cols):
                childs = []
                if self.mapp[r][c] == "*":
                    continue
                else:
                    if r + 1 < self.rows:
                        if self.mapp[r+1][c] != "*":
                            ind = self.rows * (r+1) + c
                            childs.append(ind)
                    if r - 1 > -1:
                        if self.mapp[r-1][c] != "*":
                            ind = self.rows * (r-1) + c
                            childs.append(ind)
                    if c + 1 < self.cols:
                        if self.mapp[r][c+1] != "*":
                            ind = self.rows * r + c + 1
                            childs.append(ind)
                    if c - 1 > -1:
                        if self.mapp[r][c-1] != "*":
                            ind = self.rows * r + c - 1
                            childs.append(ind)

                    newNode = Node(self.mapp[r][c], childs, (r, c), self.rows)
                    self.index_based_dict[(self.rows * r) + c] = newNode
                    self.childs_list.append(childs)


class SearchPath:
    def __init__(self, g: Graph):
        self.graphSize = g.rows * g.cols
        self.g = g
        self.bases = find_bases(g.mapp)
        # self.dpDistanceAndNext = [[None for _ in range(self.graphSize)] for _ in range(self.graphSize)]
        # for i in range(0, self.graphSize):
        #     self.dpDistanceAndNext[i][i] = (0, -1)
        self.frontierStart = [False for _ in range(self.graphSize)]
        self.frontierGoal = [False for _ in range(self.graphSize)]

        self.queueStart = []
        self.queueGoal = []

    def baseFind(self):
        for i in self.queueGoal:
            if i in self.bases:
                return i
        return -1

    def intersect(self):
        for i in range(self.g.rows * (self.g.rows-1) + (self.g.cols-1)):
            if self.frontierStart[i] and self.frontierGoal[i]:
                return i
        return -1

    def takeAction(self, pre: int, current: int):
        c0 = self.g.index_based_dict[pre].coordinate
        c1 = self.g.index_based_dict[current].coordinate
        if c0[0] - 1 == c1[0]:
            return Action.UP
        if c0[0] + 1 == c1[0]:
            return Action.DOWN
        if c0[1] - 1 == c1[1]:
            return Action.LEFT
        if c0[1] + 1 == c1[1]:
            return Action.RIGHT

    def actReverse(self, act):
        if act == Action.DOWN:
            return Action.UP
        if act == Action.UP:
            return Action.DOWN
        if act == Action.RIGHT:
            return Action.LEFT
        if act == Action.LEFT:
            return Action.RIGHT

    # BFS just returns (len(answer), nearestBaseIndex)
    def distanceAndNext(self, start: tuple, goal: tuple):
        back_nearestBase = self.BFS_Backward(goal)
        forward = self.BFS_Forward(start, goal)
        frw = len(forward)
        back = len(back_nearestBase[0])
        if len(forward) == 0:
            frw = float('inf')
        if len(back_nearestBase[0]) == 0:
            back = float('inf')

        return frw + back, makeTuple(self.g.cols, back_nearestBase[1])

    def BFSAndNext(self, begin: tuple, end: tuple):
        firstPath = self.BFS_Forward(begin, end)
        secondPath_next = self.BFS_Backward(end)
        if len(firstPath) == 0 or len(secondPath_next[0]) == 0:
            return [], (-1, -1)
        return firstPath + secondPath_next[0], makeTuple(secondPath_next[1])

    def BFS(self, begin: tuple, end: tuple):
        path = self.BFS_Forward(begin, end)
        if len(path) == 0:
            return []
        return path

    def BFS_NoWall(self, begin: tuple, end: tuple):
        path = self.BFS_Forward_No_Wall(begin, end)
        if len(path) == 0:
            return []
        return path

    def OLDBFS(self, begin: tuple, end: tuple):
        firstPath = self.BFS_Forward(begin, end)
        secondPath = self.BFS_Backward(end)[0]
        if len(firstPath) == 0:
            return []
        if len(secondPath) == 0:
            return []
        return firstPath + secondPath

    def BFS_Forward(self, begin: tuple, end: tuple):
        self.frontierStart = [False for _ in range(self.graphSize)]
        self.queueStart = []

        start = makeScallar(self.g.cols, *begin)
        goal = makeScallar(self.g.cols, *end)

        self.frontierStart[start] = True
        self.queueStart.append(start)
        while len(self.queueStart) != 0:
            current = self.queueStart.pop(0)
            children = self.g.index_based_dict[current].childs
            for child in children:
                aDiamond = isDiamond(self.g.mapp[makeTuple(self.g.cols, child)[0]][makeTuple(self.g.cols, child)[1]])
                if (not self.frontierStart[child]) and ((not aDiamond) or (aDiamond and child == goal)):
                    self.queueStart.append(child)
                    self.frontierStart[child] = True
                    self.g.index_based_dict[child].parentSrc = current
                    self.g.index_based_dict[child].actionSrc = self.takeAction(current, child)


        answer = []
        if not self.frontierStart[goal]:
            return answer
        temp_it = goal
        while temp_it != start:
            answer.insert(0, self.g.index_based_dict[temp_it].actionSrc)
            temp_it = self.g.index_based_dict[temp_it].parentSrc
        return answer


    def BFS_Backward(self, begin: tuple):
        self.frontierGoal = [False for _ in range(self.graphSize)]
        self.queueGoal = []
        goal = makeScallar(self.g.cols, *begin)

        self.frontierGoal[goal] = True
        self.queueGoal.append(goal)

        nearestBaseIndex = self.baseFind()

        while len(self.queueGoal) != 0 and nearestBaseIndex == -1:
            current = self.queueGoal.pop(0)
            children = self.g.index_based_dict[current].childs
            for child in children:
                if not self.frontierGoal[child]:
                    self.queueGoal.append(child)
                    self.frontierGoal[child] = True
                    self.g.index_based_dict[child].parentGoal = current
                    self.g.index_based_dict[child].actionGoal = self.takeAction(current, child)
            nearestBaseIndex = self.baseFind()
        answer = []
        if not self.frontierGoal[goal]:
            return answer
        temp_it = nearestBaseIndex
        while temp_it != goal:
            answer.insert(0, self.g.index_based_dict[temp_it].actionGoal)
            temp_it = self.g.index_based_dict[temp_it].parentGoal

        return answer, nearestBaseIndex

    def BFS_Forward_No_Wall(self, begin: tuple, end: tuple):
        self.frontierStart = [False for _ in range(self.graphSize)]
        self.queueStart = []

        start = makeScallar(self.g.cols, *begin)
        goal = makeScallar(self.g.cols, *end)

        self.frontierStart[start] = True
        self.queueStart.append(start)
        while len(self.queueStart) != 0:
            current = self.queueStart.pop(0)
            children = self.g.index_based_dict[current].childs
            for child in children:
                aDiamond = isDiamond(self.g.mapp[makeTuple(self.g.cols, child)[0]][makeTuple(self.g.cols, child)[1]])

                if not self.frontierStart[child]:
                    self.queueStart.append(child)
                    self.frontierStart[child] = True
                    self.g.index_based_dict[child].parentSrc = current
                    self.g.index_based_dict[child].actionSrc = self.takeAction(current, child)


        answer = []
        if not self.frontierStart[goal]:
            return answer
        temp_it = goal
        while temp_it != start:
            answer.insert(0, self.g.index_based_dict[temp_it].actionSrc)
            temp_it = self.g.index_based_dict[temp_it].parentSrc
        return answer


def find_diamonds_bases(bmap):
    diamonds = []
    bases = []
    for r in range(len(bmap)):
        for c in range(len(bmap[r])):
            if isDiamond(bmap[r][c]):
                diamonds.append((r, c))
            if bmap[r][c] == "a":
                bases.append(r * len(bmap) + c)
    return diamonds, bases


def find_bases_tuple(bmap):
    bases = []
    for r in range(len(bmap)):
        for c in range(len(bmap[r])):
            if bmap[r][c] == "a":
                bases.append((r, c))
    return bases


def find_bases(bmap):
    bases = []
    for r in range(len(bmap)):
        for c in range(len(bmap[r])):
            if bmap[r][c] == "a":
                bases.append(r * len(bmap) + c)
    return bases


def find_diamonds(bmap):
    diamonds = []
    for r in range(len(bmap)):
        for c in range(len(bmap[r])):
            if isDiamond(bmap[r][c]):
                diamonds.append((bmap[r][c], (r, c)))
    return diamonds

def isDiamond(x):
    if x == '0' or x == '1' or x == '2' or x == '3' or x == '4':
        return True
    return False

def value(d):
    values = [2, 5, 3, 1, 10]
    return values[int(d)]


def makeScallar(m: int, x: int, y: int):
    return m * x + y


def makeTuple(m: int, index: int):
    return (index // m), (index % m)


def printMap(map):
    for i in range(len(map)):
        for j in range(len(map[i])):
            print(map[i][j], end="")
        print()
    print(".....................")

def joinLists(a: list, b: list):
    i = 0
    j = 0
    index = 0
    ans = []
    while index < len(a) + len(b):
        if index % 2 == 0:
            ans.append(a[i])
            i += 1
        else:
            ans.append(b[j])
            j += 1
        index += 1
    return ans