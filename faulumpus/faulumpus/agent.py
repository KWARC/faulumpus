


class Agent(object):
    def __init__(self, name):
        self.name = name

    def onGameStart(self):
        pass
    
    def onGameEnd(self, score, message):
        pass

    def getMove(self, world):
        return None


class RandomAgent(Agent):
    def __init__(self, risk=0.05):
        Agent.__init__(self, 'Random')
        self.risk = risk

    def getMove(self, world):
        import random
        options = [s for s in world.squares() if not s.discovered and any(n.discovered and ((not n.breeze) or random.random() < self.risk) for n in s.neighbours.values())]
        if options:
            s = random.choice(options)
            return (s.x, s.y)
        else:
            return None
