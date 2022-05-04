from collections import UserDict
from pathlib import Path


class Paths(UserDict):
    def __init__(self) -> None:
        self.home = Path.home() / '.netease_arrange'

        super().__init__(dict(
            cookies=self.home / '.cookies',
            api_data=self.home / '.api_data',
            data=self.home / '.data',
            converter=self.home.parent / 'converter.exe'
        ))

    def init(self, account: str) -> None:
        (self.home / account).mkdir(parents=True, exist_ok=True)
        for key, value in self.data.items():
            if key != 'converter':
                self.data[key] = value.parent / account / value.name
                self.data[key].touch(exist_ok=True)

        if not self.data['cookies'].stat().st_size:
            self.data['cookies'].write_text('#LWP-Cookies-2.0\n')


paths = Paths()
