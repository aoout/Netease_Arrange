import json
from collections import UserDict
from pathlib import Path
from typing import Optional


class DataDict(UserDict):
    def __init__(self, path: str or Path,
                 default_value: dict = dict(),
                 encoding: Optional[str] = None,
                 ensure_ascii: bool = True) -> None:
        super().__init__(default_value)
        path = Path(path)
        self.path = path
        self.encoding = encoding
        self.ensure_ascii = ensure_ascii

    def read(self) -> None:
        if self.path.stat().st_size:
            self.data = json.loads(self.path.read_text(encoding=self.encoding))

    def write(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=self.ensure_ascii), encoding=self.encoding)


def diff_dict(a: dict, b: dict) -> dict:
    a_keys_set = set(a.keys())
    b_keys_set = set(b.keys())
    return {
        "+": list(b_keys_set - a_keys_set),
        "-": list(a_keys_set - b_keys_set)
    }


def diff_list(a: list, b: list) -> dict:
    a_set = set(a)
    b_set = set(b)
    return {
        "+": list(b_set - a_set),
        "-": list(a_set - b_set)
    }
