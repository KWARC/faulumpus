import requests
from server import SECRET_PATH
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from agent import *

class FAULumpusConnection(object):
    def __init__(self, name, key, address):
        self.session = requests.session()
        self.name = name
        self.key = key
        self.address = address
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def makeMoves(self, moves):
        # TODO: Verify that moves is non-empty and that moves are well-formed
        response = self.session.put(f'{self.address}/{SECRET_PATH}',
                data = f'name: {self.name}\nkey: {self.key}\nmoves: {"; ".join(moves)}')
        response.raise_for_status()

        # score is always 0, unless game is over
        result = {'squares': [], 'gameover': False, 'reason-of-gameover': None, 'score': 0}

        inGameOver = False
        for line in response.text.splitlines():
            line = line.strip()
            if line == 'SQUARE':
                result['squares'].append({})
            elif line == 'GAME OVER':
                inGameOver = True
                result['gameover'] = True
            elif ':' in line:
                sep = line.index(':')
                key = line[:sep].strip()
                val = line[sep+1:].strip()
                if inGameOver:
                    if key == 'Reason':
                        result['reason-of-gameover'] = val
                    elif key == 'Score':
                        result['score'] = int(val)
                    # ignore unsupported keys
                else:
                    if key in ['X', 'Y']:
                        val = int(val)
                    elif key in ['IsSight', 'Pit', 'Breeze', 'Smell', 'Wumpus'] and val in ['True', 'False']:
                        val = True if val == 'True' else False
                    result['squares'][-1][key] = val
            else:
                raise Exception(f'Unexpected line: "{line}"')
        return result


    def newGame(self):
        response = self.session.post(f'{self.address}/{SECRET_PATH}',
                data = f'name: {self.name}\nkey: {self.key}')
        response.raise_for_status()
        square = {}
        for line in response.text.splitlines():
            line = line.strip()
            if line == 'SQUARE':
                continue
            elif ':' in line:
                sep = line.index(':')
                key = line[:sep].strip()
                val = line[sep+1:].strip()
                if key in ['X', 'Y']:
                    val = int(val)
                elif key in ['IsSight', 'Pit', 'Breeze', 'Smell', 'Wumpus'] and val in ['True', 'False']:
                    val = True if val == 'True' else False
                square[key] = val
        return square

if __name__ == '__main__':
    import sys, os
    args = sys.argv[1:]
    STEP = False
    LOCAL = True
    for arg in args:
        if arg == '-step':
            STEP = True
        elif arg == '-compete':
            LOCAL = False
        else:
            print(f'Unknown option {arg}')

    connection = FAULumpusConnection(AGENT_NAME, AGENT_PASSWORD, f'http://127.0.0.1:{os.environ.get("PORT", "8000")}' if LOCAL else 'https://faulumpus.kwarc.info')

    gamecounter = 0
    scores = []
    while True:
        if STEP: input('Press <Return> to continue...')
        firstSquare = connection.newGame()
        AGENT.onGameStart(firstSquare)
        gameOver = False
        while not gameOver:
            if STEP: input('Press <Return> to continue...')
            moves = AGENT.getMoves()
            result = connection.makeMoves(moves)
            AGENT.onDiscoveredSquares(result['squares'])
            if result['gameover']:
                gameOver = True
                scores.append(result['score'])
                AGENT.onGameEnd(result['score'], result['reason-of-gameover'])
                print(f'Result of game {gamecounter}: {result["score"]} ({result["reason-of-gameover"]})')
                print(f'Average score: {sum(scores)/len(scores)}')
                gamecounter += 1

