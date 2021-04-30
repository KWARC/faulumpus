from enum import Enum
from random import random, randint, choice
import tkinter

WIDTH = 6
HEIGHT = 6
TILESIZE = 50

LEFT  = 0
UP    = 1
RIGHT = 2
DOWN  = 3


GRASS = 'grass'
SWAMP = 'swamp'
STONE = 'stone'

class Square(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.smell = False
        self.type = GRASS
        self.wumpus = False
        self.echo = False
        self.gold = False
        self.discovered = False
        self.pit = False

        self.neighbours = {}

    def draw(self, canvas):
        canvas.delete('all')
        if not self.discovered:
            canvas.configure(bg = '#aaaaaa')
            canvas.create_text(TILESIZE/2, TILESIZE/2, anchor='c', text='?')
            return
        canvas.configure(bg = {GRASS: '#009900', SWAMP: '#113355', STONE: '#555555'}[self.type])
        if self.gold:
            canvas.create_oval(TILESIZE*0.3, TILESIZE*0.3, TILESIZE*0.7, TILESIZE*0.7, fill='#cccc00')

    def astuples(self):
        return [('Coordinates', (self.x, self.y)),
                ('Type', self.type),
                ('Gold', self.gold),
                ('Smell', self.smell),
                ('Wumpus', self.wumpus),
                ('Echo', self.echo),
                ('Pit', self.pit)]

    def __str__(self):
        return '\n'.join([f'{k+":":13}{v}' for k,v in self.astuples()])





class World(object):
    def __init__(self):
        self.world = {(x,y):Square(x,y) for x in range(WIDTH) for y in range(HEIGHT)}

        # link neighbours
        for x,y in self.world:
            for d,c in [(LEFT, (x-1,y)), (RIGHT, (x+1,y)), (UP, (x,y-1)), (DOWN, (x,y+1))]:
                if c in self.world:
                    self.world[(x,y)].neighbours[d] = self.world[c]

        self.playerx = 0
        self.playery = 0
        self.world[(self.playerx, self.playery)].discovered = True



def getLegalSquare(isbanned, maxreps=50):
    for i in range(maxreps):
        x,y = (randint(0,WIDTH-1), randint(0, HEIGHT-1))
        if not isbanned(x,y):
            return (x,y)
    return None


