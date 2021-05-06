# Your task is to implement a new agent.
# `TimidAgent` (see below) is a very simple example agent.
class Agent(object):
    def onGameStart(self, firstSquare):
        '''
            This method is called when a new game is started.
            `firstSquare` contains information on the square that you landed on in the form of a dictionary.
            Here is an example:
            {
                'X': 0,                       # X coordinate
                'Y': 0,                       # Y coordinate
                'Type': 'grass',              # not very important
                'IsSight': True,              # the square contains a sight
                'NameOfSight': 'Südmensa',    # name of the sight (irrelevant)
                'Smell': False,               # no smell here
                'Wumpus': False,              # no Wumpu here either (fortunately)
                'Breeze': True,               # there is a breeze here
                'Pit': False                  # no pit here (fortunately)
            }
        '''
        pass
    
    def onGameEnd(self, score, reason):
        '''
            This method is called when a game ends. You don't have to do anything here.
            `score`: The number of points you get.
            `reason`: The reason why the game has ended ('Finish', 'Pit', 'Wumpus' or 'IllegalMove').
        '''
        pass

    def onDiscoveredSquares(self, squares):
        '''
            You performed some moves (see `getMoves`) and discovered some squares.
            `squares`: a list of dictionaries describing the discovered squares (see also `onGameStart`).
        '''
        pass

    def getMoves(self):
        '''
            Here you should return a list of moves.
            A move is a string:
                'FINISH' means that you want to end the game and get your points.
                '5,2' means that you want to explore square (5, 2). Other coordinates are analogous.
            You can return a single move in the list (e.g. ['FINISH']).
            To save time, you can also return multiple moves at once (e.g. ['2,3', '2,4', '3,3']).
        '''
        pass


class TimidAgent(Agent):
    ''' A simple example agent that walks to the right until it senses any danger '''
    def onGameStart(self, firstSquare):
        # self.x and self.y are used to store the current position
        self.x = firstSquare['X']
        self.y = firstSquare['Y']
        self.keepWalking = True
        if firstSquare['Smell'] or firstSquare['Breeze']:
            # don't keep walking if there might be any danger
            self.keepWalking = False

    def onGameEnd(self, score, reason):
        print('I got ' + str(score) + ' points!')

    def onDiscoveredSquares(self, squares):
        for square in squares:
            # update current position
            self.x = square['X']
            self.y = square['Y']
            # don't keep walking if there might be any danger
            if square['Smell'] or square['Breeze']:
                self.keepWalking = False

    def getMoves(self):
        if self.x == 11:  # end of world
            return ['FINISH']
        if not self.keepWalking:
            return ['FINISH']
        return [str(self.x + 1) + ',' + str(self.y)]



# TODO: Adjust these.
# Please only use ASCII characters.
# The password should be more than 10 characters long.
# We don't store the password safely, so you should definitely not reuse a password from elsewhere!
AGENT_NAME = 'MrTimid'
AGENT_PASSWORD = ''
AGENT = TimidAgent()

