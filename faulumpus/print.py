import pickle
import gzip
import time
import os.path
import re
import csv
import sys

def getstats():
    AGENT_STATS = { }
    lastsave = int(time.time())

    if not os.path.isdir('saved'):
        return AGENT_STATS, lastsave
    
    filenameregex = re.compile('^' + '[0-9]'*12 + r'-saved\.dmp$')
    files = [f for f in os.listdir('saved') if filenameregex.match(f)]
    files.sort()
    if files:
        with gzip.open(os.path.join('saved', files[-1]), 'rb') as fp:
            AGENT_STATS = pickle.load(fp)
        lastsave = int(files[-1][:12])

    return AGENT_STATS, lastsave

if __name__ == "__main__":
    stats, _ = getstats()

    data = []
    for user, ud in stats.items():
        data.append([user, ud["key"], ud["maxscore"]])
    
    data = sorted(data, key=lambda item: -item[2])
    writer = csv.writer(sys.stdout)
    writer.writerows(data)

# grading
# Points:
#
# > 0 => 0
# > 1 => 50
# > 2 => 75
# > 3 => 100
# > 4 => 125
# > 5 => 150
# > 6 => 175
# > 7 => 200
#
# Missing description => -25 points