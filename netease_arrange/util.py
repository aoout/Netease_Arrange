# pylint:disable = missing-module-docstring,invalid-name
import json
from collections import UserDict
from pathlib import Path
from typing import Optional, List


class DataDict(UserDict):
    '''
    dict that can be used to storage data.
    '''

    def __init__(self, path: str or Path,
                 default_value: Optional[dict] = None,
                 encoding: Optional[str] = None,
                 ensure_ascii: bool = True) -> None:
        super().__init__(default_value if default_value else {})
        path = Path(path)
        self.path = path
        self.encoding = encoding
        self.ensure_ascii = ensure_ascii

    def read(self) -> None:
        '''
        read data from the path to dict.
        '''
        if self.path.stat().st_size:
            self.data = json.loads(self.path.read_text(encoding=self.encoding))

    def write(self) -> None:
        '''
        write the dict's data to the path.
        '''
        self.path.write_text(json.dumps(
            self.data, ensure_ascii=self.ensure_ascii), encoding=self.encoding)


def diff_dict(a: dict, b: dict) -> dict:
    '''
    compare increased keys or decreased keys between two dicts.
    '''
    a_keys_set = set(a.keys())
    b_keys_set = set(b.keys())
    return {
        "+": list(b_keys_set - a_keys_set),
        "-": list(a_keys_set - b_keys_set)
    }


def diff_list(a: list, b: list) -> dict:
    '''
    compare increases or decreases between two lists.
    '''
    a_set = set(a)
    b_set = set(b)
    return {
        "+": list(b_set - a_set),
        "-": list(a_set - b_set)
    }


def to_pathname(path: str) -> str:
    '''
    convert a string to a valid windows path.
    '''
    return ''.join([c for c in path if c not in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']])


def is_json(string: str) -> bool:
    '''
    check if the string is a json string.
    '''
    try:
        json.loads(string)
        return True
    except:  # pylint:disable = bare-except
        return False


def split_list(list_: list, max_length: int) -> List[list]:
    '''
    split the string to multi-strings, so that everyone has a max-lenght.
    '''
    result = []
    i = 0
    while i < len(list_):
        result.append(list_[i:i+max_length])
        i += max_length
    return result

def init_lwpcookiejar(path:str or Path)->None:
    '''
    init LWPCookieJar.
    '''
    path = Path(path)
    path.write_text('#LWP-Cookies-2.0\n') #pylint:disable =unspecified-encoding