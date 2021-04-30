


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


class BasicAgent(Agent):
    def __init__(self):
        Agent.__init__(self, 'Basic')

    def getMove(self, world):
        fringe = {s for s in world.squares() if not s.discovered and any(n.discovered for n in s.neighbours.values())}
        safetoexplore = {s for s in fringe if any(n.discovered and not n.breeze for n in s.neighbours.values())}
        if safetoexplore:
            s = safetoexplore.pop()
            return (s.x, s.y)
        score = sum(1 if s.issight else 0 for s in world.squares() if s.discovered)
        if score == 0 or score == 1:
            s = fringe.pop()
            return (s.x, s.y)
        return None


