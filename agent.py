import random
from base import BaseAgent, TurnData, Action
from ExhaustiveSearch import *
# from SearchPath import *


class Agent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.solution = []
        self.diamonds_cors = []
        self.base_cors = []
        self.graph = None
        self.algo = None
        self.state = 0
        self.diamond_permutation = None
        self.dIndex = 0
        self.position = None

    def do_turn(self, turn_data: TurnData) -> Action:
        if self.state == 0:
            agent_coordinate = turn_data.agent_data[0].position
            self.diamonds_cors = find_diamonds(turn_data.map)
            self.base_cors = find_bases_tuple(turn_data.map)
            self.graph = Graph(len(turn_data.map), len(turn_data.map[0]), turn_data.map)
            self.graph.fillChilds()
            self.algo = ExhaustiveSearch(self.graph)
            self.diamond_permutation = self.algo.bestDiamondPermutation(agent_coordinate, turn_data.turns_left,
                                                                        self.diamonds_cors, self.base_cors)
            print("diamonds :", self.diamonds_cors)
            print("selected permutation :", self.diamond_permutation)
            self.solution = self.algo.searchPath.BFS(
                agent_coordinate, self.diamond_permutation[self.dIndex][1])
            print(self.solution)
            self.dIndex += 1

            act = self.solution.pop(0)
            if len(self.solution):
                self.state = 2
            else:
                self.state = 1
                if self.dIndex % 2 == 1:
                    self.algo.searchPath.g.fillXY(self.diamond_permutation[self.dIndex - 1][1][0],
                                                  self.diamond_permutation[self.dIndex - 1][1][1], '.')
            return act

        if self.state == 1:
            agent_pos = turn_data.agent_data[0].position
            if self.dIndex % 2 == 0:
                goal = self.diamond_permutation[self.dIndex][1]
            else:
                goal = self.diamond_permutation[self.dIndex]
            if self.dIndex % 2 == 0:
                self.solution = self.algo.searchPath.BFS(agent_pos, goal)
            else:
                self.solution = self.algo.searchPath.BFS_NoWall(agent_pos, goal)
            print(self.solution)
            self.dIndex += 1

            act = self.solution.pop(0)
            if len(self.solution):
                self.state = 2
            else:
                self.state = 1
                if self.dIndex % 2 == 1:
                    self.algo.searchPath.g.fillXY(self.diamond_permutation[self.dIndex - 1][1][0],
                                                  self.diamond_permutation[self.dIndex - 1][1][1], '.')
            return act

        if self.state == 2:
            # we have a solution and we will use it until it's empty
            if self.solution:
                if len(self.solution) == 1:
                    self.state = 1
                    if self.dIndex % 2 == 1:
                        self.algo.searchPath.g.fillXY(self.diamond_permutation[self.dIndex - 1][1][0], self.diamond_permutation[self.dIndex - 1][1][1], '.')
                act = self.solution.pop(0)
                return act



if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)
