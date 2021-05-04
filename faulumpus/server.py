from http.server import HTTPServer, BaseHTTPRequestHandler
import re

GAMES_FOR_EVAL = 1000

SECRET_PATH = 'cfa2189a2c00a70b81e59319d7442303'   # ''.join([hex(random.randint(0,255))[2:].rjust(2,'0') for i in range(16)])

# 'name' : {'key': ..., 'results': [...], 'maxscore': ... }
AGENT_STATS = {

}


GAMES = {

}

from generate import WorldGenerator
GENERATOR = WorldGenerator()

name_regex = re.compile(r'^[a-zA-Z0-9 -_!.()]+$')
key_regex = re.compile(r'^[a-zA-Z0-9]+$')
move_regex = re.compile(r'^\d+,\s*\d+$')

def squareSerialize(square):
    return 'SQUARE\n' + '\n'.join([f'{k}: {v}' for (k,v) in square.astuples()])

def gameOver(name, score):
    del GAMES[name]
    s = AGENT_STATS[name]
    s['results'].append(score)
    if len(s['results']) > GAMES_FOR_EVAL:
        del s['results'][0]
        maxscore = sum(s['results'])/GAMES_FOR_EVAL
        if maxscore > s['maxscore']:
            s['maxscore'] = maxscore

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def contentlines(self):
        ''' returns None in case of error. Also checks for authorization and creates entry in AGENT_STATS if necessary '''
        if SECRET_PATH not in self.path:
            self.send_error(404)
            return None
        if 'Content-Length' not in self.headers:
            self.send_error(411, 'Content-Length not specified')
            return None
        content = self.rfile.read(int(self.headers['Content-Length'])).decode('UTF-8')
        d = {}
        for line in content.splitlines():
            if not ':' in line:
                self.send_error(400, 'Malformed request: expected ":" in each line')
                return None
            sep = line.index(':')
            key = line[:sep].strip()
            val = line[sep+1:].strip()
            d[key] = val
        if not 'name' in d:
            self.send_error(400, 'Malformed request: no name specified')
            return None
        if not 'key' in d:
            self.send_error(400, 'Malformed request: no key specified')
            return None
        if not name_regex.match(d['name']):
            self.send_error(400, 'Malformed request: illegal name')
            return None
        if not key_regex.match(d['key']):
            self.send_error(400, 'Malformed request: illegal key')
            return None
        name = d['name']
        key = d['key']
        if name in AGENT_STATS:
            if AGENT_STATS[name]['key'] != key:
                self.send_error(403, 'An agent with that name exists already (your key is wrong)')
                return None
        else:
            AGENT_STATS[name] = {
                        'key' : key,
                        'results' : [],
                        'maxscore' : 0.0,
                    }

        return d

    def do_PUT(self):
        d = self.contentlines()
        if d == None:
            return
        if not 'moves' in d:
            self.send_error(400, 'Malformed request: no moves specified')
            return
        name = d['name']
        if name not in GAMES:
            self.send_error(404, 'No game for this agent found')
            return
        w = GAMES[d['name']]
        m = d['moves']

        messages = []

        for move in m.split(';'):
            move = move.strip()
            if move == 'FINISH':
                score = w.getScore()
                messages.append(f'GAME OVER\nReason: Finish\nScore: {score}')
                gameOver(name, score)
                break
            elif not move_regex.match(move):
                self.send_error(400, f'Malformed request: invalued move "{move}"')
                return
            else:
                move = move.split(',')
                x = int(move[0].strip())
                y = int(move[1].strip())
                if not w.canBeDiscovered(x, y):
                    messages.append(f'GAME OVER\nReason: IllegalMove\nScore: 0')
                    gameOver(name, 0)
                    break
                w[x,y].discovered = True
                messages.append(squareSerialize(w[x,y]))
                if w[x,y].pit:
                    messages.append(f'GAME OVER\nReason: Pit\nScore: 0')
                    gameOver(name, 0)
                    break

        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n'.join(messages).encode('UTF-8'))

    def do_POST(self):
        d = self.contentlines()
        if d == None:
            return
        w = GENERATOR.makeWorld()  # note: can't have pit at [0,0]
        name = d['name']
        if name in GAMES:
            gameOver(name, GAMES[name].getScore())
        GAMES[name] = w
        message = squareSerialize(w[0,0])
        self.send_response(200, message)
        self.end_headers()


if __name__ == '__main__':
    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()


