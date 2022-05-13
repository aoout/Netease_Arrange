from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List


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
        from .Record import record
        diff = diff_list(record['depository']['old'], self.local_songs_path)
        record['depository']['old'] = self.local_songs_path

        record['netease']['deleting'] += diff_list(
            record['netease']['deleting'], diff['-'])['+']

    def convert_name_format(self) -> None: 
        for song in self.local_songs_path:
            for suffix in ('.mp3', '.flac'):
                if (path := self.path / Path(song).with_suffix(suffix)).exists():
                    file_name_parts = path.stem.split(' - ')
                    file_name_parts.reverse()
                    new_file_name = ' - '.join(file_name_parts)
                    path.rename(path.with_stem(new_file_name))
