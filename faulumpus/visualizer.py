from world import Square
import queue
import tkinter


class Visualizer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.queue = queue.Queue()

    def run(self):
        self.TILESIZE = 30
        self.name = f'FAULumpus Visualizer'
        self.world = None
        self.gameover = False

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
        for x in range(self.width):
            for y in range(self.height):
                self.cmap[(x,y)] = tkinter.Canvas(squareLabel, width=self.TILESIZE, height=self.TILESIZE)
                self.cmap[(x,y)].grid(column=x,row=self.height-y)
                self.cmap[(x,y)].bind('<Enter>', (lambda x,y:lambda e : onEnter(x,y))(x,y))
                self.cmap[(x,y)].bind('<Leave>', (lambda x,y:lambda e : onLeave(x,y))(x,y))
        squareDetailsKeys = tkinter.StringVar()
        squareDetailsKeysLabel = tkinter.Label(self.window, textvariable=squareDetailsKeys, width=10, bg='white', justify=tkinter.LEFT)
        squareDetailsKeysLabel.grid(column=1, row=0, sticky='SN')
        squareDetailsKeys.set('\n'.join([e[0]+':' for e in Square(0,0).astuples()]))
        squareDetailsValues = tkinter.StringVar()
        squareDetailsValuesLabel = tkinter.Label(self.window, textvariable=squareDetailsValues, width=10, bg='white', justify=tkinter.LEFT, anchor='w')
        squareDetailsValuesLabel.grid(column=2, row=0, sticky='SN')
        self.showHidden = False
        def sethidden(b):
            self.showHidden = b
            return True
        self.window.bind('<KeyPress-Control_L>', lambda e : sethidden(True) and self.drawWorld())
        self.window.bind('<KeyRelease-Control_L>', lambda e : sethidden(False) and self.drawWorld())

        while True:
            if not self.queue.empty():
                (world, highlight) = self.queue.get()
                self._drawWorld(world, highlight)
                self.queue.task_done()
            self.window.update_idletasks()
            self.window.update()

        # self.window.mainloop()

    def drawWorld(self, world=None, highlight=[]):
        self.queue.put((world, highlight))


    def _drawWorld(self, world = None, highlight = []):
        if world:
            self.world = world
        if not self.world:
            return
        for square in self.world.squares():
            square.draw(self.cmap[(square.x, square.y)], self.TILESIZE, self.showHidden)
        size = self.TILESIZE
        for (x, y) in highlight:
            self.cmap[(x,y)].create_line(size*0.1,size*0.9,size*0.9,size*0.9,fill='#00aa00',width=size*0.15)

