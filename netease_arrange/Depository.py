from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .JsonDataFile import json_data_file
from .LocalSong import LocalSong
from .Song import Songs


class Depository():

    def __init__(self, path: Path or str) -> None:
        path = Path(path)
        self.path = path

    @cached_property
    def local_songs(self) -> List[LocalSong]:
        songs = Songs()
        for sp in list(chain(*[self.path.glob(f'**/*.{suffix}') for suffix in ['flac', 'mp3']])):
            song = LocalSong(sp)
            songs.append(song)
        return songs

    def diff(self) -> None:
        songs_now = set(self.local_songs.names)
        songs_before = set(json_data_file.data['depository']['last_recorded'])
        json_data_file.data['depository']['last_recorded'] =  list(songs_now)

        songs_deleted = songs_before - songs_now
        temp = set(json_data_file.data['netease']['waitting_be_deleted'])
        json_data_file.data['netease']['waitting_be_deleted'] += list(songs_deleted - temp)
