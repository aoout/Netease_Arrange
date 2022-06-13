# pylint:disable = missing-module-docstring,line-too-long

import os
import shutil
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .Api import Api
from .Paths import Paths
from .Record import Record
from .util import diff_list


class Netease:
    '''
    manage online playlists on NetEase Cloud and their local downloaded files.
    those online songs that have a corresponding downloaded file locally are said to be accessible.
    '''

    def __init__(self, download_path: Path or str, group_playlists_prefix: List[str] = None) -> None:
        download_path = Path(download_path)
        self.download_path = download_path
        self.api = Api()
        self.group_playlists_prefix = group_playlists_prefix if group_playlists_prefix else []

    def login(self, account: str, password: str) -> None:
        '''
        log in to NetEase Cloud Music.
        '''
        self.api.login(account, password)

    def _convert(self) -> None:
        '''
        Transcode vip songs.
        '''
        if Paths()['converter']:
            vip_songs_path = self.download_path / 'VipSongsDownload'
            for vs in vip_songs_path.rglob('*.ncm'):
                if vs not in self.local_songs_name:
                    os.system(f'{Paths()["converter"]} "{vs}"')

    @cached_property
    def online_songs_path(self) -> List[str]:
        '''
        Get the path of all online songs.
        '''
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
        '''
        get name of all local music.
        '''
        songs_name = []
        for sp in chain(*(self.download_path.rglob(f'*.{suffix}') for suffix in ['flac', 'mp3'])):
            songs_name.append(str(sp.stem))
        return songs_name

    def sync(self, depository: "Depository"):
        '''
        sync.
        '''
        diff = diff_list(Record()['netease']['old'], self.online_songs_path)
        self.dispatch(depository, diff)

        self.delete(depository, diff)

    def dispatch(self, depository, diff):
        '''
        dispatch accessible songs to repositories.
        '''
        Record()['netease']['old'] = self.online_songs_path

        songs_to_assign = set(
            Record()['netease']['unavailable']) | set(diff['+'])
        songs_to_assign_actually = {
            song for song in songs_to_assign if self.accessible(song)}
        Record()['netease']['unavailable'] = list(
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
        '''
        determine if an online song is locally accessible.
        '''
        online_song_path = Path(online_song_path)
        return online_song_path.stem in self.local_songs_name

    def delete(self, depository, diff):
        '''
        delete the song files in the repository that should be deleted.
        for example, the songs may have been deleted from the NetEase Cloud account.
        '''
        songs_be_deleted = set(
            diff['-']) & set(Record()['netease']['deleting'])
        songs_to_delete = set(diff['-']) - set(Record()['netease']['deleting'])
        Record()['netease']['deleting'] = list(
            set(Record()['netease']['deleting']) - songs_be_deleted - set(Record()['netease']['last_deleted']))
        Record()['netease']['last_deleted'] = list(songs_to_delete)
        for i in songs_to_delete:
            i = Path(i)
            for suffix in ('.mp3', '.flac'):
                if (depository.path / i.with_suffix(suffix)).exists():
                    os.remove(depository.path / i.with_suffix(suffix))

    def convert_name_format(self) -> None:
        '''
        convert the file name like "artist-song name" or "song name-artist" to each other.
        '''
        for song in self.local_songs_name:
            for suffix in ('.mp3', '.flac'):
                if (path := self.download_path / Path(song).with_suffix(suffix)).exists():
                    file_name_parts = path.stem.split(' - ')
                    file_name_parts.reverse()
                    new_file_name = ' - '.join(file_name_parts)
                    path.rename(path.with_stem(new_file_name))
