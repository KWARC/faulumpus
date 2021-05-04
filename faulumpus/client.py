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
        response = self.session.put(f'http://localhost:8000/{SECRET_PATH}',
                data = f'name: {self.name}\nkey: {self.key}\nmoves: {"; ".join(moves)}')
        response.raise_for_status()
        print(response.text)


    def newGame(self):
        response = self.session.post(f'http://localhost:8000/{SECRET_PATH}',
                data = f'name: {self.name}\nkey: {self.key}')
        response.raise_for_status()

if __name__ == '__main__':
    connection = FAULumpusConnection('John', 'asdf')
    print('making new game')
    connection.newGame()
    print('making first move')
    connection.makeMoves(['0,1', 'FINISH'])


