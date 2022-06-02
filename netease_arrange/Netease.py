import os
import shutil
from functools import cached_property
from itertools import chain
from pathlib import Path
from tkinter import N
from typing import List

from .Api import Api
from .Paths import paths

from .util import diff_list


class Netease:

    def __init__(self, download_path: Path or str, group_playlists_prefix: List[str] = list()) -> None:
        download_path = Path(download_path)
        self.download_path = download_path
        self.group_playlists_prefix = group_playlists_prefix

    def login(self, account: str, password: str) -> None:
        self.api = Api(account, password)

    def _convert(self) -> None:
        if paths['converter']:
            self.vip_songs_path = self.download_path / 'VipSongsDownload'
            for vs in self.vip_songs_path.rglob('*.ncm'):
                if vs not in self.local_songs_name:
                    os.system(f'{paths["converter"]} "{vs}"')

    @cached_property
    def online_songs_path(self) -> List[str]:
        self.api.update()
        songs_path = []
        for playlist_name, songs in self.api.data.items():
            for song_name, song in songs.items():
                file_name = song_name + ' - ' + ','.join(
                    [ar['name'] for ar in song['artists']])
                for prefix in self.group_playlists_prefix:
                    if playlist_name.startswith(f'{prefix}，'):
                        parent_path = Path(
                            *playlist_name.split('，', maxsplit=1))
                        break
                else:
                    parent_path = Path(playlist_name)

                songs_path.append(str(parent_path / Path(file_name)))

        return songs_path

    @cached_property
    def local_songs_name(self) -> List[str]:
        songs_name = []
        for sp in chain(*(self.download_path.rglob(f'*.{suffix}') for suffix in ['flac', 'mp3'])):
            songs_name.append(str(sp.stem))
        return songs_name

    def sync(self, depository: "Depository"):
        from .Record import record
        diff = diff_list(record['netease']['old'], self.online_songs_path)
        self.assign(depository, diff)

        self.delete(depository, diff)

    def assign(self, depository, diff):
        from .Record import record
        record['netease']['old'] = self.online_songs_path

        songs_to_assign = set(record['netease']['unavailable']) | set(diff['+'])
        songs_to_assign_actually = set(
            [song for song in songs_to_assign if self.accessible(song)])
        record['netease']['unavailable'] = list(
            songs_to_assign-songs_to_assign_actually)

        for song in songs_to_assign_actually:
            song = Path(song)
            for suffix in ('.mp3', '.flac'):
                if (src := (self.download_path / Path(song.name).with_suffix(suffix))).exists():

                    dst = depository.path / song.with_suffix(suffix)
                    if not dst.parent.exists():
                        dst.parent.mkdir(parents=True)
                    shutil.copy(src, dst)

    def accessible(self, online_song_path: str) -> bool:
        online_song_path = Path(online_song_path)
        return online_song_path.stem in self.local_songs_name

    def delete(self, depository, diff):
        from .Record import record
        songs_be_deleted = set(diff['-']) & set(record['netease']['deleting'])
        songs_to_delete = set(diff['-']) - set(record['netease']['deleting'])
        record['netease']['deleting'] = list(
            set(record['netease']['deleting']) - songs_be_deleted - set(record['netease']['last_deleted']))
        record['netease']['last_deleted'] = list(songs_to_delete)
        for i in songs_to_delete:
            i = Path(i)
            for suffix in ('.mp3', '.flac'):
                if (depository.path / i.with_suffix(suffix)).exists():
                    os.remove(depository.path / i.with_suffix(suffix))

    def convert_name_format(self) -> None:
        for song in self.local_songs_name:
            for suffix in ('.mp3', '.flac'):
                if (path := self.download_path / Path(song).with_suffix(suffix)).exists():
                    file_name_parts = path.stem.split(' - ')
                    file_name_parts.reverse()
                    new_file_name = ' - '.join(file_name_parts)
                    path.rename(path.with_stem(new_file_name))
