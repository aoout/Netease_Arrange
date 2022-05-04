from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .Record import record
from .util import diff_list


class Depository():

    def __init__(self, path: Path or str) -> None:
        path = Path(path)
        self.path = path

    @cached_property
    def local_songs_path(self) -> List[str]:
        songs_path = []
        for s in chain(*(self.path.rglob(f'*.{suffix}') for suffix in ('flac', 'mp3'))):
            songs_path.append(str((s.relative_to(self.path)).with_suffix('')))
        return songs_path

    def diff(self) -> None:
        diff = diff_list(record['depository']['old'], self.local_songs_path)
        record['depository']['old'] = self.local_songs_path

        record['netease']['deleting'] += diff_list(record['netease']['deleting'],diff['-'])['+']

