import os
import shutil
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .Api import Api
from .Paths import paths
from .Record import record
from .util import diff_list


class Netease:

    def __init__(self, download_path: Path or str, account: str, password: str) -> None:
        download_path = Path(download_path)
        self.download_path = download_path
        if paths['converter'].exists():
            self._convert()
        self.api = Api(account, password)

    def _convert(self) -> None:
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
                file_name = ','.join(
                    [ar['name'] for ar in song['artists']]) + ' - ' + song_name
                songs_path.append(str(Path(playlist_name, file_name)))

        return songs_path

    @cached_property
    def local_songs_name(self) -> List[str]:
        songs_name = []
        for sp in chain(*(self.download_path.rglob(f'*.{suffix}') for suffix in ['flac', 'mp3'])):
            songs_name.append(str(sp.stem))
        return songs_name

    def sync(self, depository: "Depository"):
        diff = diff_list(record['netease']['old'], self.online_songs_path)
        self.assign(depository, diff)

        self.delete(depository, diff)

    def assign(self, depository, diff):

        record['netease']['old'] = self.online_songs_path

        songs_to_assign = set(record['netease']['block']) | set(diff['+'])
        songs_to_assign_actually = set(
            [song for song in songs_to_assign if self.accessible(song)])
        record['netease']['block'] = list(
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
