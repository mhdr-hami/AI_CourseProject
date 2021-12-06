from tools import *


class Agent:
    def __init__(self, point: tuple):
        self.point = point


class World:
    def __init__(self, diamondsno: int, agentpos: tuple, checklist: list, hashBase: int):

        self.checklist = checklist
        self.diamondsno = diamondsno
        self.resdiamondsno = diamondsno
        self.resagentpos = agentpos
        self.hashBase = hashBase
        self.agent = Agent(agentpos)

    def makeHash(self, l: list) -> int:
        hashing = 0
        for i in range(len(l)):
            hashing += (self.hashBase ** i) * int(l[i])
        return hashing

    def stepping(self, action: int):
        return

    def reset(self):
        self.checklist = [0 for _ in range(self.resdiamondsno)]
        self.agent = Agent(self.resagentpos)
        self.diamondsno = self.resdiamondsno
        return 0
