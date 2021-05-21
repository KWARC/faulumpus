from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import time
import pickle
import os
import gzip
import hashlib

GAMES_FOR_EVAL = 1000
SECRET_PATH = 'cfa2189a2c00a70b81e59319d7442303'   # ''.join([hex(random.randint(0,255))[2:].rjust(2,'0') for i in range(16)])
AGENT_STATS = { }                                  # 'name' : {'key': ..., 'results': [...], 'maxscore': ... }
GAMES = { }                                        # 'name' : World

from generate import WorldGenerator
GENERATOR = WorldGenerator()

VISUALIZER = None

def save_agentstats():
    timestamp = str(int(time.time())).rjust(12, '0')
    with gzip.open(os.path.join('saved', f'{timestamp}-saved.dmp'), 'wb') as fp:
        pickle.dump(AGENT_STATS, fp)
    save_agentstats.lastsave = time.time()
    save_agentstats.uptodate = True
    
    # remove unecessary files:
    files = [f for f in os.listdir('saved') if filenameregex.match(f)]
    files.sort()
    last = 0
    for f in files[:-1]:
        this = int(f[:12])
        if this-last < 60*60 or (time.time() - this > 48 * 60 * 60 and this-last < 12*60*60):
            os.remove(os.path.join('saved', f))
        else:
            last = this

def maybe_save_agentstats(change = False):
    if change:
        save_agentstats.uptodate = False
    if (not save_agentstats.uptodate) and time.time() - save_agentstats.lastsave > 60*2:
        save_agentstats()

# try loading AGENT_STATS
if not os.path.isdir('saved'):
    os.mkdir('saved')
filenameregex = re.compile('^' + '[0-9]'*12 + r'-saved\.dmp$')
files = [f for f in os.listdir('saved') if filenameregex.match(f)]
files.sort()
if files:
    with gzip.open(os.path.join('saved', files[-1]), 'rb') as fp:
        AGENT_STATS = pickle.load(fp)
    save_agentstats.lastsave = int(files[-1][:12])
else:
    save_agentstats.lastsave = int(time.time())
save_agentstats.uptodate = True


name_regex = re.compile(r'^[a-zA-Z0-9 _!()\.-]+$')
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
        if not name_regex.match(d['name']) or len(d['name']) > 30:
            self.send_error(400, 'Malformed request: illegal name')
            return None
        if not key_regex.match(d['key']) or not (10 < len(d['key']) < 500):
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
                        'maxscore' : -1.0,  # not evaluated
                    }

        return d

    def do_GET(self):
        maybe_save_agentstats(False)
        self.send_response(200)
        self.end_headers()
        content = [f'<html>\n<body>\n<h1>FAULumpus</h1>']
        if os.environ.get('IT_IS_OVER') == '1':
            content.append("<h2 style='color: red'>The assignment is now over. You can still play games and add new scores, but they will not be counted. However, we may shut down the server in the future without any notice. </h2>")
        content.append('''<p>
This is the FAULumpus test server for the <a href="https://kwarc.info/teaching/AI/">AI 2 lecture</a> at <a href="https://www.fau.de/">FAU</a>.
The source code and further information can be found in the <a href="https://github.com/kwarc/faulumpus">Github repository</a>.
</p>''')
        content.append('<img src="https://nc.kwarc.info/s/GA3MdQTx7oY6FLn/download" alt="Example wumpus world">')
        content.append(f'<h2>Evaluated Agents (requires {GAMES_FOR_EVAL} games)</h2>')
        content.append(f'<p>The evaluation score of an agent is the maximal average score of {GAMES_FOR_EVAL} consecutive games. Therefore, the evaluation will be updated when your agent becomes stronger and you do not have to get a new name for your agent.</p>')
        content.append('<ol>')
        for agent in sorted((n for n in AGENT_STATS if AGENT_STATS[n]['maxscore'] > -0.5), key=lambda n : -AGENT_STATS[n]['maxscore']):
            s = AGENT_STATS[agent]
            hk = hashlib.sha256(s['key'].encode('UTF-8')).hexdigest()
            content.append(f'<li>{agent}<!-- {hk} -->: {AGENT_STATS[agent]["maxscore"]:.4}</li>')
        content.append('</ol>')
        content.append(f'<h2>Agents with less than {GAMES_FOR_EVAL} Games</h2>\n<ul>')
        for agent in AGENT_STATS:
            s = AGENT_STATS[agent]
            if s['maxscore'] < -0.5:
                score = 0.0 if not s['results'] else sum(s['results'])/len(s['results'])
                hk = hashlib.sha256(s['key'].encode('UTF-8')).hexdigest()
                content.append(f'<li>{agent}<!-- {hk} -->: {score:.4} (average from {len(s["results"])} games)</li>')
        content.append('</ul>')
        content.append(f'<p><small>Last backup: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(save_agentstats.lastsave))} UTC<br/>Changes since last backup: {"No " if save_agentstats.uptodate else "Yes"}</small></p>')
        content.append('</body>\n</html>')

        self.wfile.write('\n'.join(content).encode('UTF-8'))


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
        discovered = []

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
                discovered.append((x,y))
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
                if w[x,y].wumpus:
                    messages.append(f'GAME OVER\nReason: Wumpus\nScore: 0')
                    gameOver(name, 0)
                    break

        if VISUALIZER:
            VISUALIZER.drawWorld(w, discovered)
        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n'.join(messages).encode('UTF-8'))
        maybe_save_agentstats(True)

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

        if VISUALIZER:
            VISUALIZER.drawWorld(w, [(0,0)])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message.encode('UTF-8'))
        maybe_save_agentstats(True)




if __name__ == '__main__':
    import os, sys, signal

    # when requested, start the visualizer
    if sys.argv[-1] == '-visualize':
        import visualizer
        VISUALIZER = visualizer.Visualizer(GENERATOR.width, GENERATOR.height)
        import threading
        threading.Thread(target=VISUALIZER.run).start()

    # setup code to gracefully stop the server!
    def stop_gracefully(sig, frame):
        print("Received signal {}, saving and exiting gracefully. ".format(sig))
        save_agentstats()
        sys.exit(1)

    signal.signal(signal.SIGINT, stop_gracefully)
    signal.signal(signal.SIGTERM, stop_gracefully)

    # Create the server
    hostname = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '8000'))

    httpd = HTTPServer((hostname, port), SimpleHTTPRequestHandler)
    print("Listening on {}:{}".format(hostname, port))

    try:
        httpd.serve_forever()
    finally:
        save_agentstats()

