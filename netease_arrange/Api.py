import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict

from .constant import constant
from .raw_api import RawApi


@dataclass
class ApiArtist:
    name: str
    id: int


@dataclass
class ApiSong:
    name: str
    id: int
    artists: List[ApiArtist]


@dataclass
class ApiPlayLists:
    playlists: Dict[str, List[ApiSong]]


class Api:
    def __init__(self, account: str, password: str) -> None:

        if os.path.getsize(constant.api_data_path ) == 0:
            self.data = ApiPlayLists({})
        else:
            self.data = ApiPlayLists(json.loads(constant.api_data_path .read_text(encoding='utf-8')))

        if self._update(account, password):
            self._write()

    def _update(self, account: str, password: str) -> bool:
        if login_r := RawApi.login(account, password):
            user_id = login_r.json()['account']['id']
            if playlists_r := RawApi.get_playlists(user_id):
                self._playlists_id, self._playlists_name = ([pl[field] for pl in playlists_r.json()['playlist']] for
                                                            field in ('id', 'name'))

                for key in set(self._playlists_name) | set(self.data.playlists.keys()):
                    if key not in set(self.data.playlists.keys()):
                        self.data.playlists[key] = []
                    elif key not in self._playlists_name:
                        del self.data.playlists[key]

                self._get_songs_name()
                return True
        return False

    def _write(self) -> None:
        constant.api_data_path.write_text(json.dumps(asdict(self.data), ensure_ascii=False), encoding='utf-8')

    def _get_songs_name(self) -> None:
        for pl_id, pl_name in zip(self._playlists_id, self._playlists_name):
            if songs_r := RawApi.get_songs_from_playlist(pl_id):

                for sg in songs_r.json()['playlist']['tracks']:
                    name = sg['name']
                    id_ = sg['id']
                    artists = [ApiArtist(ar['name'], ar['id']) for ar in sg['ar']]
                    song = ApiSong(name, id_, artists)
                    self.data.playlists[pl_name] += [song]
            else:
                break
