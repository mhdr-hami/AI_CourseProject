import random
import math
import numpy as np
from base import BaseAgent, TurnData, Action
from Minimax import *
from tools import *

def toAction(x: str):
    if x == "UP":
        return Action.UP
    if x == "DOWN":
        return Action.DOWN
    if x == "LEFT":
        return Action.LEFT
    if x == "RIGHT":
        return Action.RIGHT


class Agent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.solution = []
        self.state = 0
        self.maximumTurns = 0
        self.firstTime = True
        self.g = None
        self.tools = None

    def do_turn(self, turn_data: TurnData) -> Action:
        print(turn_data.agent_data[0].count_required, ".........................")
        if self.state == 0:
            if self.firstTime:
                self.maximumTurns = turn_data.turns_left
                self.firstTime = False
            diamonds, bases = find_diamonds_bases(turn_data.map, turn_data.agent_data[0])
            self.g = Graph(len(turn_data.map), len(turn_data.map[0]), turn_data.map)
            self.g.fillChilds()
            self.tools = SearchPath(self.g)
            rootState = State([], turn_data.agent_data, 0, self.maximumTurns, diamonds, bases)
            SumOfAllDiamonds = 0
            for i in diamonds:
                SumOfAllDiamonds += value(i[0])
            miniMaxAlgo = Minimax(turn_data.agent_data[0].count_required, self.maximumTurns, turn_data.agent_data, self.tools, SumOfAllDiamonds)
            self.act = miniMaxAlgo.Minimax_Decision(rootState, len(turn_data.agent_data))
            print("act ", self.act)
            if self.act == None:
                return Action.RIGHT
            self.solution = self.tools.BFS(turn_data.agent_data[0].position, self.act[0][1])
            self.solution += self.tools.BFS_NoWall(self.act[0][1], self.act[1])
            # self.solution = []
            self.state = 1
            return self.solution.pop(0)
        if self.state == 1:
            if self.solution:
                if len(self.solution) == 1:
                    self.state = 0
                    last_diamond = self.act[0]
                    self.tools.g.fillXY(last_diamond[1][0], last_diamond[1][1], '.')
                act = self.solution.pop(0)
            else:
                while 1:
                    return Action.UP
            return act


if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)
