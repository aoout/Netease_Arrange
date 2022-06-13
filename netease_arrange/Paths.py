# pylint:disable = missing-module-docstring
from collections import UserDict
from pathlib import Path

from .util import Singleton, init_lwpcookiejar

@Singleton
class Paths(UserDict):
    '''
    manager all the path that project need to use.
    '''

    def init(self, account: str) -> None:
        home = Path.home() / '.netease_arrange' / account
        home.parent.mkdir(exist_ok=True)
        home.mkdir(exist_ok=True)
        self.data['converter'] = home.parent / 'converter.exe'
        for path in ['cookies', 'api_data', 'data']:
            self.data[path] = home / f'.{path}'
            self.data[path].touch()

        if not self.data['cookies'].stat().st_size:
            init_lwpcookiejar(self.data['cookies'])
