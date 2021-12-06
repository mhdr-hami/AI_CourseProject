import random
import helper
import numpy as np
import math
from base import BaseAgent, TurnData, Action
import RL


class Agent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.solution = []
        self.diamonds_cors = []
        self.base_cors = []
        self.searchPath = None
        self.graph = None
        self.algo = None
        self.state = 0
        self.diamond_permutation = None
        self.dIndex = 0
        self.position = None

    def do_turn(self, turn_data: TurnData) -> Action:
        if self.state == 0:
            agent_coordinate = turn_data.agent_data[0].position
            checklist = [0 for _ in range(len(self.diamonds_cors))]
            self.diamonds_cors = RL.tools.find_diamonds(turn_data.map)
            self.base_cors = RL.tools.find_bases_tuple(turn_data.map)
            self.graph = RL.tools.Graph(len(turn_data.map), len(turn_data.map[0]), turn_data.map)
            self.graph.fillChilds()
            self.searchPath = RL.tools.SearchPath(self.graph)
            self.algo = RL.Qlearning(self.diamonds_cors, self.base_cors, turn_data.turns_left, agent_coordinate,
                                     checklist, self.graph, self.searchPath)

            self.diamond_permutation = self.algo.learn()


            if len(self.diamond_permutation) == 1:
                last = self.diamond_permutation[0]
                self.diamond_permutation.append(self.searchPath.distanceAndNext(agent_coordinate, last[1])[1])
            print("diamonds :", self.diamonds_cors)
            print("selected permutation :", self.diamond_permutation)
            self.solution = self.searchPath.BFS(
                agent_coordinate, self.diamond_permutation[self.dIndex][1])
            print(self.solution)

            if self.dIndex + 1 < len(self.diamond_permutation):
                self.dIndex += 1

            act = self.solution.pop(0)
            if len(self.solution):
                self.state = 2
            else:
                self.state = 1
                if self.dIndex % 2 == 1:
                    self.searchPath.g.fillXY(self.diamond_permutation[self.dIndex - 1][1][0],
                                                  self.diamond_permutation[self.dIndex - 1][1][1], '.')
            return act

        if self.state == 1:
            agent_pos = turn_data.agent_data[0].position
            if self.dIndex % 2 == 0:
                goal = self.diamond_permutation[self.dIndex][1]
            else:
                goal = self.diamond_permutation[self.dIndex]
            self.solution = self.searchPath.BFS_NoWall(agent_pos, goal)
            print(self.solution)
            if self.dIndex + 1 < len(self.diamond_permutation):
                self.dIndex += 1
            if len(self.solution):
                act = self.solution.pop(0)
            else:
                return Action.UP
            if len(self.solution):
                self.state = 2
            else:
                self.state = 1
                if self.dIndex % 2 == 1:
                    self.searchPath.g.fillXY(self.diamond_permutation[self.dIndex - 1][1][0],
                                                  self.diamond_permutation[self.dIndex - 1][1][1], '.')
            return act

        if self.state == 2:
            # we have a solution and we will use it until it's empty
            if self.solution:
                if len(self.solution) == 1:
                    self.state = 1
                    if self.dIndex % 2 == 1:
                        self.searchPath.g.fillXY(self.diamond_permutation[self.dIndex - 1][1][0], self.diamond_permutation[self.dIndex - 1][1][1], '.')
                act = self.solution.pop(0)
                return act



if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)
