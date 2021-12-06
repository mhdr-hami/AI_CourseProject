from tools import *
import sys
import copy
from base import BaseAgent, TurnData, Action


class State:
    def __init__(self, state_diamonds: list, agents: list, agent_id, remainingTurns, allDiamonds: list, allBases: list):
        self.stateDiamonds = copy.deepcopy(state_diamonds)
        self.agents = copy.deepcopy(agents)
        self.agent_id = agent_id
        self.value = 0
        self.parent = None
        self.children = []
        self.remainingTurns = remainingTurns
        self.allBases = copy.deepcopy(allBases)
        self.allDiamonds = copy.deepcopy(allDiamonds)
        # self.correspondingAction = None
        # self.carring = [False for i in range(len(agents))]

    def isQuiescent(self):
        # Rule 2
        tempList = [self.stateDiamonds[i] for i in range(0, len(self.stateDiamonds), 2)]
        if (len(tempList) >= 3 and len(set(tempList[len(tempList) - 3:])) == 3) or \
            ((len(tempList) >= 4 and len(set(tempList[len(tempList) - 4:]))) == 4):
            return False
        # Finishing Turns
        if self.remainingTurns <= 2:
            return False
        # Finishing Diamonds
        if len(self.allDiamonds) == 1:
            return False
        return True

    def isTerminal(self, total_turn):
        print("isTerminal ? ", self.stateDiamonds)
        if self.remainingTurns <= 0:
            return True

        ourDiamonds = [self.stateDiamonds[i] for i in range(0, len(self.stateDiamonds), 2)]
        diamonds_set = set(ourDiamonds[len(ourDiamonds) - 4:])
        if len(diamonds_set) == 5:
            return True

        # Finishing Diamonds
        if len(self.allDiamonds) == 0:
            return True

        return False

    def Utility(self, required_diamonds, max_turns, tools: SearchPath, startingAgentPos):
        fit_value = 0
        taken = []
        agent_pos = startingAgentPos
        passedTurns = 0
        total_diamond = [0, 0, 0, 0, 0]
        coEfficients = [0, 0, 0, 0, 0]

        for d in range(0, len(self.stateDiamonds), 2):
            total_diamond[int(self.stateDiamonds[d][0])] += 1

        for r_d in range(len(required_diamonds)):
            if required_diamonds[r_d] <= total_diamond[r_d]:
                coEfficients[r_d] = 1

        for i in range(len(self.stateDiamonds)):
            gene = self.stateDiamonds[i]
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
                # base
                dist = len(tools.BFS_NoWall(agent_pos, gene))
                if dist == 0:
                    dist = float('inf')
                else:
                    agent_pos = gene
            if dist + passedTurns <= max_turns:
                passedTurns += dist
                if i % 2 == 1:
                    fit_value = fit_value + coEfficients[int(self.stateDiamonds[i - 1][0])] * value(self.stateDiamonds[i - 1][0])
            else:
                break
            for j in taken:
                tools.g.fillXY(self.stateDiamonds[j][1][0], self.stateDiamonds[j][1][1], self.stateDiamonds[j][0])
        print("stateDiamonds", self.stateDiamonds)
        print("fitval", fit_value)
        return fit_value

    def Actions_in_decision(self, tools: SearchPath):
        actions = []
        for diamond in self.allDiamonds:
            dist, base = tools.distanceAndNext(self.agents[self.agent_id].position, diamond[1], self.agents[self.agent_id])
            print(dist , base , "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            if dist <= self.remainingTurns:
                actions.append((diamond, base, dist))
            # actions.append(diamond)
            # actions.append(base)
        return actions

    def Actions(self, tools: SearchPath):
        actions = []
        for diamond in self.allDiamonds:
            dist, base = tools.distanceAndNext(self.agents[self.agent_id].position, diamond[1], self.agents[self.agent_id])
            if dist <= self.remainingTurns:
                # self.remainingTurns -= dist
                actions.append((diamond, base, dist))
            # actions.append(diamond)
            # actions.append(base)
        return actions

    def Actions_2(self, tools: SearchPath):
        actions = []
        for diamond in self.allDiamonds:
            dist, base = tools.distanceAndNext(self.agents[self.agent_id].position, diamond[1], self.agents[self.agent_id])
            dist2, base2 = tools.distanceAndNext(self.agents[0].position, diamond[1], self.agents[self.agent_id])
            if dist <= self.remainingTurns and dist <= dist2:
                # self.remainingTurns -= dist
                actions.append((diamond, base, dist))
            # actions.append(diamond)
            # actions.append(base)
        return actions

    def Result(self, action, tools: SearchPath):
        # diamond should be deleted from map
        diamond, base, dist = action
        new_state = State(self.stateDiamonds, self.agents, self.agent_id, self.remainingTurns,
                          self.allDiamonds, self.allBases)
        # diamond and its base should be added to stateDiamond

        new_state.stateDiamonds.append(diamond)
        new_state.stateDiamonds.append(base)
        new_state.agents[self.agent_id].position = base
        new_state.agent_id = (new_state.agent_id + 1) % len(new_state.agents)
        new_state.remainingTurns -= dist
        new_state.allDiamonds.remove(diamond)
        return new_state
