import os
import shutil
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import List

from .Api import Api
from .JsonDataFile import json_data_file


class Netease:

    def __init__(self, download_path: Path or str, account: str, password: str) -> None:
        download_path = Path(download_path)
        self.download_path = download_path

        self._api = Api(account, password)

    @cached_property
    def online_songs_path(self) -> List[str]:
        songs_path = []
        for pl_name, pl_songs in self._api.data.playlists.items():
            for sg in pl_songs:
                songs_path.append(str(Path(pl_name, ','.join([ar.name for ar in sg.artists]) + ' - ' + sg.name)))
        return songs_path

    @cached_property
    def local_songs_name(self) -> List[str]:
        songs_name = []
        for sp in chain(*(self.download_path.rglob(f'*.{suffix}') for suffix in ['flac', 'mp3'])):
            songs_name.append(str(sp.stem))
        return songs_name

    def sync(self, depository: "Depository"):
        online_songs_now = set(self.online_songs_path)
        online_songs_before = set(json_data_file.data['netease']['last_recorded'])
        online_songs_added = online_songs_now - online_songs_before
        online_songs_deleted = online_songs_before - online_songs_now
        json_data_file.data['netease']['last_recorded'] = list(online_songs_now)

        songs_waitting_resources = set(json_data_file.data['netease']['waitting_resources'])
        songs_to_copy = set()
        for sp in (songs_waitting_resources | online_songs_added):
            sp = Path(sp)
            if sp.stem in self.local_songs_name:
                songs_to_copy.add(str(sp))

        songs_waitting_resources = (songs_waitting_resources | online_songs_added) - songs_to_copy

        json_data_file.data['netease']['waitting_resources'] = list(songs_waitting_resources)

        for sp in songs_to_copy:
            sp = Path(sp)
            for suffix in ('.mp3', '.flac'):
                if (self.download_path / Path(sp.name).with_suffix(suffix)).exists():
                    src = self.download_path / Path(sp.name).with_suffix(suffix)
                    dst = depository.path / sp.with_suffix(suffix)
                    if not dst.parent.exists():
                        dst.parent.mkdir(parents=True)
                    shutil.copy(src, dst)

        songs_waitting_be_deleted = set(json_data_file.data['netease']['waitting_be_deleted'])
        songs_be_deleted = online_songs_deleted & songs_waitting_be_deleted
        songs_to_delete = online_songs_deleted - songs_waitting_be_deleted
        temp = set(json_data_file.data['netease']['last_deleted'])
        json_data_file.data['netease']['waitting_be_deleted'] = list(
            songs_waitting_be_deleted - songs_be_deleted - temp)
        json_data_file.data['netease']['last_deleted'] = list(songs_to_delete)

        for sp in songs_to_delete:
            sp = Path(sp)
            for suffix in ('.mp3', '.flac'):
                if (depository.path / sp.with_suffix(suffix)).exists():
                    os.remove(depository.path / sp.with_suffix(suffix))
