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
        self._api = Api(account, password)

    def _convert(self) -> None:
        self.vip_songs_path = self.download_path / 'VipSongsDownload'
        for vs in self.vip_songs_path.rglob('*.ncm'):
            if vs not in self.local_songs_name:
                os.system(f'{paths["converter"]} "{vs}"')

    @cached_property
    def online_songs_path(self) -> List[str]:
        songs_path = []
        for pl_name, pl_songs in self._api.data.items():
            for sg in pl_songs:
                songs_path.append(
                    str(Path(pl_name, ','.join([ar['name'] for ar in sg['artists']]) + ' - ' + sg['name'])))
        return songs_path

    @cached_property
    def local_songs_name(self) -> List[str]:
        songs_name = []
        for sp in chain(*(self.download_path.rglob(f'*.{suffix}') for suffix in ['flac', 'mp3'])):
            songs_name.append(str(sp.stem))
        return songs_name

    def sync(self, depository: "Depository"):
        diff = diff_list(record['netease']['old'], self.online_songs_path)
        record['netease']['old'] = self.online_songs_path

        songs_to_copy = set()
        for i in (set(record['netease']['block']) | set(diff['+'])):
            i = Path(i)
            if i.stem in self.local_songs_name:
                songs_to_copy.add(str(i))

        record['netease']['block'] = list((set(record['netease']['block']) | set(diff['+'])) - songs_to_copy)

        for i in songs_to_copy:
            i = Path(i)
            for suffix in ('.mp3', '.flac'):
                if (self.download_path / Path(i.name).with_suffix(suffix)).exists():
                    src = self.download_path / Path(i.name).with_suffix(suffix)
                    dst = depository.path / i.with_suffix(suffix)
                    if not dst.parent.exists():
                        dst.parent.mkdir(parents=True)
                    shutil.copy(src, dst)

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
