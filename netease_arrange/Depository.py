from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .JsonDataFile import json_data_file


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
        songs_now = set(self.local_songs_path)
        songs_before = set(json_data_file.data['depository']['last_recorded'])
        json_data_file.data['depository']['last_recorded'] = list(songs_now)

        songs_deleted = songs_before - songs_now
        temp = set(json_data_file.data['netease']['waitting_be_deleted'])
        json_data_file.data['netease']['waitting_be_deleted'] += list(songs_deleted - temp)
