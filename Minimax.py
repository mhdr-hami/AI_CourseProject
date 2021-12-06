from tools import *
import sys
import copy
from base import BaseAgent, TurnData, Action
from State import *
from K_Means import Clusters_Value


class Minimax:
    def __init__(self, requiredDiamonds, total_turns, agents, tool: SearchPath, MPV):
        self.requiredDiamonds = requiredDiamonds
        self.total_turns = total_turns
        self.agentsList = agents
        self.agentStartingPosition = self.agentsList[0].position
        self.tool = tool
        self.agent_id = 0
        self.MPV = MPV

    def Minimax_Decision(self, state: State, agent_num):
        if state.isTerminal(self.total_turns):
            print("why????????????????????????????????")
            state.value = state.Utility(self.requiredDiamonds, self.total_turns, self.tool, self.agentStartingPosition)
            return None
        print("0:", self.agent_id)
        currentActions = state.Actions_in_decision(self.tool)
        print("currentActions in decision", currentActions)
        index = -1
        for act in currentActions:
            state.children.append(state.Result(act, self.tool))

        best_node = state.children[0]
        # Alpha = -sys.maxsize
        # Beta = +sys.maxsize
        for c in range(len(state.children)):

            child = state.children[c]
            backupColor = currentActions[c][0][0]
            self.tool.g.fillXY(currentActions[c][0][1][0], currentActions[c][0][1][1], '.')
            self.Min_Value(child, 1) #min ??
            self.tool.g.fillXY(currentActions[c][0][1][0], currentActions[c][0][1][1], backupColor)

            if child.value > best_node.value:
                best_node = child
                index = c
            # if best_node.value >= Beta:
            #     state.value = best_node.value
            #     return state
            # Alpha = max(Alpha, best_node.value)
        return currentActions[index]

    def Max_Value(self, state: State, depth):
        self.agent_id = ((self.agent_id + 1) % len(self.agentsList))
        print("Max:", self.agent_id)
        if state.isTerminal(self.total_turns):
            print("why????????????????????????????????")
            state.value = state.Utility(self.requiredDiamonds, self.total_turns, self.tool, self.agentStartingPosition)
            return state
        if self.Cut_Off_Test(state, depth, self.total_turns):
            temp = self.Eval(state)
            return state
        best_val = - sys.maxsize
        currentActions = state.Actions(self.tool)

        # if agent_num == 1:
        #     for act in currentActions:
        #         best_val = max(best_val, self.Max_Value(state.Result(act), agent_num, alpha, beta, depth + 1))
        # else:
        f = None
        if ((self.agent_id) % len(self.agentsList)) == 0:
            f = self.Max_Value
            print("again max")
        else:
            f = self.Min_Value # min?
            print("go to min")
        for act in currentActions:
            state.children.append(state.Result(act, self.tool))
            backupColor = act[0][0]
            self.tool.g.fillXY(act[0][1][0], act[0][1][1], '.')
            best_val = max(best_val, f(state.children[-1], depth + 1).value)
            self.tool.g.fillXY(act[0][1][0], act[0][1][1], backupColor)
            # if best_val >= Beta:
            #     state.value = best_val
            #     return state
            # Alpha = max(Alpha, best_val)
        state.value = best_val
        return state

    def Min_Value(self, state: State, depth):

        self.agent_id = ((self.agent_id + 1) % len(self.agentsList))
        print("Min:", self.agent_id)
        if state.isTerminal(self.total_turns):
            print("why????????????????????????????????")
            state.value = state.Utility(self.requiredDiamonds, self.total_turns, self.tool, self.agentStartingPosition)
            return state
        if self.Cut_Off_Test(state, depth, self.total_turns):
            temp = self.Eval(state)
            return state
        best_val = + sys.maxsize
        currentActions_2 = state.Actions_2(self.tool)


        # Alpha = alpha
        # Beta = beta
        f = None
        if ((self.agent_id) % len(self.agentsList)) == 0:
            f = self.Max_Value
            print("back to max")
        else:
            f = self.Min_Value

            print("again min")

        for act in currentActions_2:
            state.children.append(state.Result(act, self.tool))
            backupColor = act[0][0]
            self.tool.g.fillXY(act[0][1][0], act[0][1][1], '.')
            best_val = min(best_val, f(state.children[-1], depth + 1).value)
            self.tool.g.fillXY(act[0][1][0], act[0][1][1], backupColor)
            # if best_val <= Alpha:
            #     state.value = best_val
            #     return state
            # Beta = min(Beta, best_val)

        state.value = best_val
        return state

    def Cut_Off_Test(self, state: State, depth, total_turn):
        if state.isQuiescent():
            return True

        if depth >= 5 * len(state.agents):
            print("cutoff happened!!")
            return True

        return False

    def Eval(self, state: State):
        # TODO total diamonds
        total_turn = self.total_turns

        possible_diamonds_bases_dist = state.Actions(self.tool)
        possible_diamonds_bases = []

        for item in state.stateDiamonds:
            possible_diamonds_bases.append(item)

        for item in possible_diamonds_bases_dist:
            possible_diamonds_bases.append(item[0])
            possible_diamonds_bases.append(item[1])
        state.value = Clusters_Value([possible_diamonds_bases], possible_diamonds_bases[0][1], state, self.requiredDiamonds, self.tool, self.MPV)[0]
        return state.value
        # fit_value = 0
        # taken = []
        # agent_pos = self.agentsList[0].position
        # passedTurns = 0
        # for i in range(len(possible_diamonds_bases)):
        #     gene = possible_diamonds_bases[i]
        #     if i % 2 == 0:
        #         # diamond
        #         dist = len(self.tool.BFS(agent_pos, gene[1]))
        #         self.tool.g.fillXY(gene[1][0], gene[1][1], '.')
        #         taken.append(i)
        #         if dist == 0:
        #             dist = float('inf')
        #         else:
        #             agent_pos = gene[1]
        #     else:
        #         # base
        #         dist = len(self.tool.BFS_NoWall(agent_pos, gene))
        #         if dist == 0:
        #             dist = float('inf')
        #         else:
        #             agent_pos = gene
        #     if dist + passedTurns <= self.total_turns:
        #         passedTurns += dist
        #         if i % 2 == 1:
        #             fit_value = fit_value + value(possible_diamonds_bases[i - 1][0])
        #     else:
        #         break
        #     for j in taken:
        #         self.tool.g.fillXY(possible_diamonds_bases[j][1][0], possible_diamonds_bases[j][1][1], possible_diamonds_bases[j][0])
        # state.value = fit_value
        # return state.value






