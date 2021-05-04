import requests
from server import SECRET_PATH
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class FAULumpusConnection(object):
    def __init__(self, name, key):
        self.session = requests.session()
        self.name = name
        self.key = key
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def makeMoves(self, moves):
        # TODO: Verify that moves is non-empty and that moves are well-formed
        response = self.session.put(f'http://localhost:8000/{SECRET_PATH}',
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
                    elif key in ['IsSight', 'Pit', 'Breeze'] and val in ['True', 'False']:
                        val = True if val == 'True' else False
                    result['squares'][-1][key] = val
            else:
                raise Exception(f'Unexpected line: "{line}"')
        return result


    def newGame(self):
        response = self.session.post(f'http://localhost:8000/{SECRET_PATH}',
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
                elif key in ['IsSight', 'Pit', 'Breeze'] and val in ['True', 'False']:
                    val = True if val == 'True' else False
                square[key] = val
        return square

if __name__ == '__main__':
    from agent import *
    import sys
    connection = FAULumpusConnection('SmartAgent2-3', 'asdf2')
    agentclassname = sys.argv[-1]
    g = globals()
    if agentclassname not in g:
        print(f'class {agentclassname} not found.')
        sys.exit(1)
    agent = g[agentclassname]()
    
    gamecounter = 0
    scores = []
    while True:
        firstSquare = connection.newGame()
        agent.onGameStart(firstSquare)
        gameOver = False
        while not gameOver:
            moves = agent.getMoves()
            result = connection.makeMoves(moves)
            agent.onDiscoveredSquares(result['squares'])
            if result['gameover']:
                gameOver = True
                scores.append(result['score'])
                agent.onGameEnd(result['score'], result['reason-of-gameover'])
                print(f'Result of game {gamecounter}: {result["score"]} ({result["reason-of-gameover"]})')
                print(f'Average score: {sum(scores)/len(scores)}')
                gamecounter += 1



