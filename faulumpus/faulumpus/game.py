import generate
from world import World, Square
from agent import *


class VisualizingAgent(object):
    def __init__(self, agent, width, height):
        import tkinter, threading
        self.TILESIZE = 30
        self.agent = agent
        self.name = f'VisualizingAgent for {agent.name}'
        self.world = None

        self.lockA = threading.Lock()
        self.lockA.acquire()
        # self.lockB = threading.Lock()
        # self.lockA.acquire()
        # self.lockB.acquire()

        def onEnter(x,y):
            if self.world:
                squareDetailsValues.set('\n'.join(str(e[1]) for e in self.world.getSquare(x,y).astuples()))
            else:
                squareDetailsValues.set('')
        def onLeave(x,y):
            squareDetailsValues.set('')

        self.window = tkinter.Tk()
        self.window.title('FAULumpus')
        self.cmap = {}
        squareLabel = tkinter.Label(self.window)
        squareLabel.grid(column=0, row=0)
        for x in range(width):
            for y in range(height):
                self.cmap[(x,y)] = tkinter.Canvas(squareLabel, width=self.TILESIZE, height=self.TILESIZE)
                self.cmap[(x,y)].grid(column=x,row=height-y)
                self.cmap[(x,y)].bind('<Enter>', (lambda x,y:lambda e : onEnter(x,y))(x,y))
                self.cmap[(x,y)].bind('<Leave>', (lambda x,y:lambda e : onLeave(x,y))(x,y))
        squareDetailsKeys = tkinter.StringVar()
        squareDetailsKeysLabel = tkinter.Label(self.window, textvariable=squareDetailsKeys, width=10, bg='white', justify=tkinter.LEFT)
        squareDetailsKeysLabel.grid(column=1, row=0, sticky='SN')
        squareDetailsKeys.set('\n'.join([e[0]+':' for e in Square(0,0).astuples()]))
        squareDetailsValues = tkinter.StringVar()
        squareDetailsValuesLabel = tkinter.Label(self.window, textvariable=squareDetailsValues, width=10, bg='white', justify=tkinter.LEFT, anchor='w')
        squareDetailsValuesLabel.grid(column=2, row=0, sticky='SN')
        # self.window.bind('<Return>', lambda e : self.lockA.release() and self.lockB.acquire() and self.lockA.acquire())
        self.window.bind('<Return>', lambda e : self.lockA.release())

    def mainloop(self):
        self.window.mainloop()

    def onGameStart(self):
        self.agent.onGameStart()

    def onGameEnd(self, score, message):
        print(score, message)
        self.agent.onGameEnd(score, message)

    def getMove(self, world):
        for square in world.squares():
            square.draw(self.cmap[(square.x, square.y)], self.TILESIZE)
        self.world = world
        self.lockA.acquire()
        return self.agent.getMove(world)



class Game(object):
    def __init__(self, agent, worldGenerator):
        self.agent = agent
        self.worldGenerator = worldGenerator

    def runGame(self):
        self.agent.onGameStart()
        score, message = self._runGameCore()
        self.agent.onGameEnd(score, message)
        return score

    def evaluate(self, iterations):
        score = 0.0
        for i in range(iterations):
            score += self.runGame()
        return score/iterations


    def _runGameCore(self):
        world = self.worldGenerator.makeWorld()
        maxMoves = world.width * world.height
        discovered = []
        
        knownworld = World(world.width, world.height, hidden=True)
        knownworld.world[(0,0)].update(world.getSquare(0,0))
        for i in range(maxMoves):
            move = self.agent.getMove(knownworld)
            if not move:
                return (len(discovered) ** 2, 'Done')
            x,y = move
            # check move
            if not (0 <= x < world.width and 0 <= y < world.height):
                return (0, f'Illegal coordinates in move: ({x}, {y})')
            if not any(n.discovered for n in world.getSquare(x,y).neighbours.values()):
                return (0, f'Illegal move: ({x}, {y}) not reachable')
            # execute move
            s = world.getSquare(x,y)
            s.discovered = True
            if s.issight and s.nameofsight not in discovered:
                discovered.append(s.nameofsight)
            knownworld.world[(x,y)].update(s)
            if s.pit:
                return (0, 'Pit')

        return (len(discovered) ** 2, 'Maximum Moves')


if __name__ == '__main__':
    generator = generate.WorldGenerator()
    agent = RandomAgent(risk = 0.0)

    import sys
    if sys.argv[-1] == 'v':
        agent = VisualizingAgent(agent, generator.width, generator.height)
        game = Game(agent, generator)
        import threading
        threading.Thread(target = lambda : game.evaluate(100)).start()
        agent.mainloop()
    else:
        game = Game(agent, generator)
        print(game.evaluate(200))
    
