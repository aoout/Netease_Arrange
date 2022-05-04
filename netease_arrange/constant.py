from pathlib import Path


class Constant:
    def __init__(self) -> None:
        self.app_name = 'netease_arrange'

    def init(self, account: str) -> None:
        self.base_path = Path.home() / f'.{self.app_name}' / account
        self.cookies_path = self.base_path / '.cookies'
        self.api_data_path = self.base_path / '.api_data'
        self.data_path = self.base_path / '.data'

        if not self.base_path.exists():
            self.base_path.mkdir()
        if not self.cookies_path.exists():
            self.cookies_path.write_text('#LWP-Cookies-2.0\n')
        if not self.api_data_path.exists():
            self.api_data_path.touch()
        if not self.data_path.exists():
            self.data_path.touch()


constant = Constant()
