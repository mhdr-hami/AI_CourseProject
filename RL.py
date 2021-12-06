import agentworld as env
import math
import random
import numpy as np
import tools
import sys


class Qlearning:
    def __init__(self, diamondslist: list, basesList: list, steps: int, agentposition: tuple, checklist: list,
                 graph: tools.Graph, tool: tools.SearchPath):
        self.diamondslist = diamondslist
        self.basesList = basesList
        self.hashBase = len(diamondslist) + len(basesList) + 1
        self.environment = env.World(len(diamondslist), agentposition, checklist, self.hashBase)
        self.qtable = dict()
        self.graph = graph
        self.tool = tool
        self.episodesnums = 2000
        self.steps = steps
        self.ressteps = steps
        self.done = False

        self.learning_rate = 0.1
        self.discount_rate = 0.99

        self.max_exploration_rate = 1
        self.min_exploration_rate = 0.1
        self.exploration_decay_rate = 0.0002

    def getanswers(self):
        for i in self.qtable:
            print(i)
        state = [0 for _ in range(2 * len(self.diamondslist))]
        index = 0
        ans = []
        while index != len(state):
            hashState = self.environment.makeHash(state)
            if index % 2 == 0:
                if max(self.qtable[hashState][:len(self.diamondslist)]) > 0:
                    state_actions = self.qtable[hashState][:len(self.diamondslist)]
                    acting = state_actions.index(max(state_actions))
                    ans.append(self.diamondslist[acting])
                    state[index] = acting + 1
            else:
                if max(self.qtable[hashState][len(self.diamondslist):]) > 0:
                    state_actions = self.qtable[hashState][len(self.diamondslist):]
                    indexOfBase = state_actions.index(max(state_actions))
                    acting = indexOfBase + len(self.diamondslist)
                    ans.append(self.basesList[indexOfBase])
                    state[index] = acting + 1
            index += 1
        return ans


    def learn(self):
        rewards_all_episodes = []
        exploration_rate = 1.0
        for episode in range(self.episodesnums):
            taken = []
            tempstate = [0 for _ in range(2 * len(self.diamondslist))]
            self.environment.reset()
            state = self.environment.makeHash(tempstate)
            self.done = False

            self.steps = self.ressteps
            if state not in self.qtable:
                self.qtable[state] = [0 for _ in range(len(self.diamondslist) + len(self.basesList))]
            rewards_current_episode = 0

            last_diamond = -1
            for i in range(2 * len(self.diamondslist)):
                if i % 2 == 0:
                    # Diamond
                    exploration_rate_threshold = np.random.uniform(0, 1)
                    if exploration_rate_threshold > exploration_rate:
                        state_actions = self.qtable[state][:len(self.diamondslist)]
                        acting = state_actions.index(max(state_actions))  # max Q rate in dict
                    else:
                        acting = random.randint(0, len(self.diamondslist)-1)
                        while self.environment.checklist[acting] == 1:
                            acting = random.randint(0, len(self.diamondslist) - 1)
                    tempstate[i] = acting + 1
                    new_state = self.environment.makeHash(tempstate)
                    if new_state not in self.qtable:
                        self.qtable[new_state] = [0 for _ in range(len(self.diamondslist) + len(self.basesList))]

                    distance = len(self.tool.BFS_Forward(self.environment.agent.point, self.diamondslist[acting][1]))
                    self.environment.agent.point = self.diamondslist[acting][1]
                    reward = 0
                    if distance == 0:
                        reward = -float('inf')
                    elif distance <= self.steps:
                        self.environment.diamondsno -= 1
                        self.steps -= distance
                        taken.append(acting)
                        self.environment.checklist[acting] = 1
                        self.tool.g.fillXY(self.diamondslist[acting][1][0], self.diamondslist[acting][1][1], '.')
                        # reward = tools.value(self.diamondslist[acting][0])
                        reward = tools.value(self.diamondslist[acting][0]) / 10
                        last_diamond = acting
                    else:
                        self.steps -= distance
                        reward = -1
                    self.qtable[state][acting] = self.qtable[state][acting] * (1 - self.learning_rate) + \
                                                 self.learning_rate * \
                                                 (reward + self.discount_rate * max(self.qtable[new_state][len(self.diamondslist):]))
                    if self.environment.diamondsno == 0:
                        self.done = True
                    if self.steps <= 0:
                        self.done = True
                    if self.done:
                        break
                    state = new_state
                    rewards_current_episode += reward
                else:
                    # i % 2 == 1
                    exploration_rate_threshold = np.random.uniform(0, 1)
                    if exploration_rate_threshold > exploration_rate:
                        state_actions = self.qtable[state][len(self.diamondslist):]
                        acting = state_actions.index(max(state_actions)) + len(self.diamondslist)  # max Q rate in dict
                    else:
                        acting = random.randint(len(self.diamondslist), len(self.diamondslist) + len(self.basesList) - 1)
                    tempstate[i] = acting + 1
                    new_state = self.environment.makeHash(tempstate)
                    if new_state not in self.qtable:
                        self.qtable[new_state] = [0 for _ in range(len(self.diamondslist) + len(self.basesList))]

                    distance = len(self.tool.BFS_Forward_No_Wall(self.environment.agent.point, self.basesList[acting - len(self.diamondslist)]))
                    self.environment.agent.point = self.basesList[acting - len(self.diamondslist)]
                    reward = 0
                    if distance == 0:
                        reward = -float('inf')
                    elif distance <= self.steps:
                        self.steps -= distance
                        reward = tools.value(self.diamondslist[last_diamond][0])
                    else:
                        self.steps -= distance
                        reward = -1
                    self.qtable[state][acting] = self.qtable[state][acting] * (1 - self.learning_rate) + \
                                                 self.learning_rate * \
                                                 (reward + self.discount_rate * max(
                                                     self.qtable[new_state][:len(self.diamondslist)]))
                    if self.environment.diamondsno == 0:
                        self.done = True
                    if self.steps <= 0:
                        self.done = True
                    if self.done:
                        break
                    state = new_state
                    rewards_current_episode += reward

            exploration_rate = self.min_exploration_rate + \
                               (self.max_exploration_rate - self.min_exploration_rate) * \
                               math.exp(-self.exploration_decay_rate * episode)
            # print(exploration_rate)
            self.steps = self.ressteps
            for i in taken:
                self.tool.g.fillXY(self.diamondslist[i][1][0], self.diamondslist[i][1][1], self.diamondslist[i][0])
            rewards_all_episodes.append(rewards_current_episode)

        return self.getanswers()
