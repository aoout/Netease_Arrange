# pylint:disable = missing-module-docstring
from collections import UserDict
from pathlib import Path
from .util import init_lwpcookiejar


class Paths(UserDict):
    '''
    manager all the path that project need to use.
    '''

    def init(self, account: str) -> None:
        '''
        according to account initialization, each account uses a different path.
        '''

        home = Path.home() / account / '.netease_arrange'
        home.mkdir(exist_ok=True)
        self.data['converter'] = home.parent / 'converter.exe'
        for path in ['cookies', 'api_data', 'data']:
            self.data[path] = home / '.'+path
            self.data[path].mkdir(exist_ok=True)

        if not self.data['cookies'].stat().st_size:
            init_lwpcookiejar(self.data['cookies'])


paths = Paths()  # implement singleton pattern.
