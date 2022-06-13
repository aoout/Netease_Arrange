# pylint:disable = missing-module-docstring
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .Record import Record
from .util import diff_list


class Depository():
    '''
    manage all the music.
    '''

    def __init__(self, path: Path or str) -> None:
        path = Path(path)
        self.path = path

    @cached_property
    def songs_path(self) -> List[str]:
        '''
        get path to all local music.
        '''
        songs_path = []
        for s in chain(*(self.path.rglob(f'*.{suffix}') for suffix in ('flac', 'mp3'))):
            songs_path.append(str((s.relative_to(self.path)).with_suffix('')))
        return songs_path

    def diff(self) -> None:
        '''
        compare with the music file situation when the program was last launched.
        '''
        diff = diff_list(Record()['depository']['old'], self.songs_path)
        Record()['depository']['old'] = self.songs_path

        Record()['netease']['deleting'] += diff_list(
            Record()['netease']['deleting'], diff['-'])['+']

    def convert_name_format(self) -> None:
        '''
        convert the file name like "artist-song name" or "song name-artist" to each other.
        '''
        for song in self.songs_path:
            for suffix in ('.mp3', '.flac'):
                if (path := self.path / Path(song).with_suffix(suffix)).exists():
                    file_name_parts = path.stem.split(' - ')
                    file_name_parts.reverse()
                    new_file_name = ' - '.join(file_name_parts)
                    path.rename(path.with_stem(new_file_name))
