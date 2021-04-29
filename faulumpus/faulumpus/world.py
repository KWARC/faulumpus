LEFT  = 'left'
UP    = 'up'
RIGHT = 'right'
DOWN  = 'down'

GRASS = 'grass'
SWAMP = 'swamp'
STONE = 'stone'

class Square(object):
    def __init__(self, x, y, hidden=False):
        self.x = x
        self.y = y
        self.smell = False if not hidden else None
        self.type = GRASS if not hidden else None
        self.wumpus = False if not hidden else None
        self.breeze = False if not hidden else None
        self.issight = False if not hidden else None
        self.nameofsight = None
        self.discovered = False
        self.pit = False if not hidden else None

        self.neighbours = {}

    def draw(self, canvas, size):
        canvas.delete('all')
        if not self.discovered:
            canvas.configure(bg = '#aaaaaa')
            canvas.create_text(size/2, size/2, anchor='c', text='?')
            return
        canvas.configure(bg = {GRASS: '#aaffaa', SWAMP: '#aaaaff', STONE: '#aaaaaa'}[self.type])
        if self.pit:
            canvas.create_oval(size*0.2, size*0.6, size*0.8, size*0.8, fill='#000000')
        if self.issight:
            canvas.create_oval(size*0.3, size*0.3, size*0.7, size*0.7, fill='#cccc00')
        if self.breeze:
            canvas.create_line(size*0.2, size*0.3, size*0.4, size*0.5, size*0.6, size*0.3, size*0.8, size*0.5, smooth=True, width=size*0.05, fill='#000000')

    def astuples(self):
        return [('Coordinates', (self.x, self.y)),
                ('Type', self.type),
                ('IsSight', self.issight),
                ('NameOfSight', self.nameofsight),
                ('Smell', self.smell),
                ('Wumpus', self.wumpus),
                ('Breeze', self.breeze),
                ('Pit', self.pit)]

    def update(self, s):
        assert self.x == s.x and self.y == s.y
        self.smell = s.smell
        self.type = s.type
        self.wumpus = s.wumpus
        self.breeze = s.breeze
        self.issight = s.issight
        self.nameofsight = s.nameofsight
        self.discovered = s.discovered
        self.pit = s.pit

    def __str__(self):
        return '\n'.join([f'{k+":":13}{v}' for k,v in self.astuples()])


class World(object):
    def __init__(self, width, height, hidden=False):
        self.width = width
        self.height = height
        self.world = {(x,y):Square(x,y, hidden) for x in range(width) for y in range(height)}

        # link neighbours
        for x,y in self.world:
            for d,c in [(LEFT, (x-1,y)), (RIGHT, (x+1,y)), (UP, (x,y-1)), (DOWN, (x,y+1))]:
                if c in self.world:
                    self.world[(x,y)].neighbours[d] = self.world[c]

        self.playerx = 0
        self.playery = 0
        self.world[(self.playerx, self.playery)].discovered = True

    def squares(self):
        return self.world.values()

    def getSquare(self, x, y):
        return self.world[(x,y)]

