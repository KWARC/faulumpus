from world import *
from random import random, randint, choice

class WorldGenerator(object):
    def __init__(self, width=12, height=8, smoothness=2.0, sights=['Schlossgarten', 'Südmensa', 'Burgberg', 'TechFak'], pitfreq = 0.2, sensorfuzziness = 0.0):
        self.width = width
        self.height = height
        self.smoothness = smoothness
        self.sights = sights
        self.pitfreq = pitfreq
        self.sensorfuzziness = sensorfuzziness
        self.stats_created = 0
        self.stats_attempted = 0

    def randomSquare(self, w):
        return w[randint(0,self.width-1), randint(0, self.height-1)]

    def getLegalSquare(self, w, isbanned, maxreps=50):
        for i in range(maxreps):
            s = self.randomSquare(w)
            if not isbanned(s):
                return s
        return None

    def makeWorld(self):
        self.stats_created += 1
        while True:
            self.stats_attempted += 1
            w = World(self.width, self.height)

            shift = random()*2-1
            for s in w.squares():
                choices = [GRASS, STONE]
                if self.width * 0.3 < s.x < self.width*0.7:
                    choices += [GRASS, GRASS]
                    if self.width * (0.35+random()/10) < s.x + shift < self.width*(0.55+random()/10):
                        choices += [SWAMP, SWAMP, SWAMP, SWAMP]
                else:
                    choices += [STONE, STONE]
                s.type = choice(choices)
                # s.type = choice([GRASS, STONE] + ([GRASS,GRASS,SWAMP,SWAMP,SWAMP] if self.width*0.3 < s.x < self.width*0.7 else [STONE]))

            for i in range(int(self.width*self.height*self.smoothness)):
                s = self.randomSquare(w)
                d = choice([LEFT, RIGHT, UP, DOWN, UP, DOWN, UP, DOWN])
                if d in s.neighbours:
                    if s.neighbours[d].type == SWAMP:
                        s.type = SWAMP
                    else:
                        s.neighbours[d].type = s.type

            for s in w.squares():
                if s.type == SWAMP and choice(list(s.neighbours.values())).type != SWAMP:
                    s.type = GRASS

            worldIsOkay = True
            for sight in self.sights:
                s = self.getLegalSquare(w, lambda s : s.type == SWAMP or s.issight)
                if not s:
                    worldIsOkay = False
                    break
                s.issight = True
                s.nameofsight = sight

            if not worldIsOkay:
                continue

            for i in range(int(self.width * self.height * self.pitfreq * (random()*0.2+0.9))):
                s = self.getLegalSquare(w, lambda s :
                            s.issight or
                            s.type == SWAMP or
                            choice(list(s.neighbours.values())).type == SWAMP or
                            choice(list(s.neighbours.values())).type == SWAMP or
                            choice(list(s.neighbours.values())).pit or
                            choice(list(s.neighbours.values())).pit or
                            choice(list(s.neighbours.values())).pit or
                            s.x+s.y==0,
                        maxreps=3)
                if not s: continue
                if s.x + s.y < random() * 5: continue  # keep starting corner free
                s.pit = True

            for s in w.squares():
                if s.pit or any(n.pit and random() > self.sensorfuzziness for n in s.neighbours.values()):
                    s.breeze = True

                if random() < self.sensorfuzziness*0.1 or s.type==STONE and random() < self.sensorfuzziness*0.1:
                    s.breeze = True

            # last tests to discard boring worlds
            if w[0,0].pit:
                continue
            oldsize = 0
            discoverable = {w[0,0]}
            while oldsize != len(discoverable):
                oldsize = len(discoverable)
                discoverable |= {s for s in w.squares() if any(n in discoverable and not n.breeze for n in s.neighbours.values())}

            if len(discoverable) > self.width * self.height * 0.4 and random() < 0.8:
                continue
            if sum((1 if s.issight else 0) for s in discoverable) == 4:
                continue
            if sum((1 if s.issight else 0) for s in discoverable) == 3 and random() < 0.5:
                continue

            return w



if __name__ == '__main__':
    TILESIZE = 30
    import tkinter
    def onEnter(x,y):
        squareDetailsValues.set('\n'.join(str(e[1]) for e in world[x,y].astuples()))
    def onLeave(x,y):
        squareDetailsValues.set('')

    generator = WorldGenerator()

    world = None
    def generateWorld(event):
        global world
        world = generator.makeWorld()
        for s in world.squares():
            s.discovered = True   # everything visible for now
        for s in world.squares():
            s.draw(cmap[(s.x, s.y)], TILESIZE)


    window = tkinter.Tk()
    window.title('FAULumpus')
    cmap = {}
    squareLabel = tkinter.Label(window)
    squareLabel.grid(column=0, row=0)
    for x in range(generator.width):
        for y in range(generator.height):
            cmap[(x,y)] = tkinter.Canvas(squareLabel, width=TILESIZE, height=TILESIZE)
            cmap[(x,y)].grid(column=x,row=generator.height-y)
            cmap[(x,y)].bind('<Enter>', (lambda x,y:lambda e : onEnter(x,y))(x,y))
            cmap[(x,y)].bind('<Leave>', (lambda x,y:lambda e : onLeave(x,y))(x,y))
    squareDetailsKeys = tkinter.StringVar()
    squareDetailsKeysLabel = tkinter.Label(window, textvariable=squareDetailsKeys, width=10, bg='white', justify=tkinter.LEFT)
    squareDetailsKeysLabel.grid(column=1, row=0, sticky='SN')
    squareDetailsKeys.set('\n'.join([e[0]+':' for e in Square(0,0).astuples()]))
    squareDetailsValues = tkinter.StringVar()
    squareDetailsValuesLabel = tkinter.Label(window, textvariable=squareDetailsValues, width=10, bg='white', justify=tkinter.LEFT, anchor='w')
    squareDetailsValuesLabel.grid(column=2, row=0, sticky='SN')
    generateWorld(None)
    window.bind('<Return>', generateWorld)



    window.mainloop()


