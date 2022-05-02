import os
import shutil
from functools import cached_property
from itertools import chain
from pathlib import Path

from .Api import Api
from .Depository import Depository
from .JsonDataFile import json_data_file
from .LocalSong import LocalSong
from .Song import Song, Songs


class OnlineSong(Song):

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.parents = []

    def add_parent(self, parent: str) -> None:
        self.parents.append(parent)


class Netease:

    def __init__(self, download_path: Path or str, account: str, password: str) -> None:
        download_path = Path(download_path)
        self.download_path = download_path
        self._account = account
        self._password = password

    @cached_property
    def online_songs(self) -> Songs:
        songs = Songs()
        for pl_name, pl_songs_name in Api(self._account, self._password).data.items():
            for sg_name in pl_songs_name:
                song = OnlineSong(sg_name)
                song.add_parent(pl_name)
                songs.append(song)
        return songs

    @cached_property
    def local_songs(self) -> Songs:
        songs = Songs()
        for sp in list(chain(*[self.download_path.glob(f'**/*.{suffix}') for suffix in ['flac', 'mp3']])):
            song = LocalSong(sp)
            songs.append(song)
        return songs

    def sync(self, depository: Depository):

        online_songs_name_now = set(self.online_songs.names)
        online_songs_name_before = set(json_data_file.data['netease']['last_recorded'])
        online_songs_name_added = online_songs_name_now - online_songs_name_before
        online_songs_name_deleted = online_songs_name_before - online_songs_name_now
        json_data_file.data['netease']['last_recorded'] = list(online_songs_name_now)

        local_songs_name_now = set(self.local_songs.names)
        songs_name_waitting_resources = set(json_data_file.data['netease']['waitting_resources'])
        songs_name_to_copy = local_songs_name_now & (songs_name_waitting_resources | online_songs_name_added)

        songs_name_waitting_resources = (songs_name_waitting_resources | online_songs_name_added) - songs_name_to_copy

        json_data_file.data['netease']['waitting_resources'] = list(songs_name_waitting_resources)

        for sm in songs_name_to_copy:
            online_songs = self.online_songs.by_name(sm)
            for os_ in online_songs:
                target = depository.path / os_.parents[0]
                if not target.exists():
                    target.mkdir()
                shutil.copy(self.local_songs.by_name(sm)[0].path, target)

        songs_name_waitting_be_deleted = set(json_data_file.data['netease']['waitting_be_deleted'])
        songs_name_be_deleted = online_songs_name_deleted & songs_name_waitting_be_deleted
        songs_name_to_delete = online_songs_name_deleted - songs_name_waitting_be_deleted
        temp = set (json_data_file.data['netease']['last_deleted'])
        json_data_file.data['netease']['waitting_be_deleted'] = list(
            songs_name_waitting_be_deleted - songs_name_be_deleted - temp)
        json_data_file.data['netease']['last_deleted'] = list(songs_name_to_delete)
        for sm in songs_name_to_delete:
            os.remove(depository.local_songs.by_name(sm)[0].path)
