import json
import os

from .constant import API_DATA_PATH
from .raw_api import RawApi


class Api:
    def __init__(self, account: str, password: str) -> None:

        if os.path.getsize(API_DATA_PATH) == 0:
            self.data = {}
        else:
            self.data = json.loads(API_DATA_PATH.read_text())

        self._update(account, password)
        self._write()

    def _update(self, account: str, password: str) -> None:
        if ac := RawApi.login(account, password).json().get('account'):
            id = ac['id']
            self._playlists_id, self._playlists_name = (
                [pl[key] for pl in RawApi.get_playlists(self._user_id).json()['playlist']] for key in ['id', 'name'])

            for key in set(self._playlists_name) | set(self.data.keys()):
                if key not in set(self.data.keys()):
                    self.data[key] = []
                elif key not in self._playlists_name:
                    del self.data[key]
            self._get_songs_name()

    def _write(self) -> None:
        API_DATA_PATH.write_text(json.dumps(self.data))

    def _get_songs_name(self) -> None:
        for pl_id, pl_name in zip(self._playlists_id, self._playlists_name):
            if pl := RawApi.get_songs_from_playlist(pl_id).json().get('playlist'):
                self.data[pl_name] = [sg['name'] for sg in pl['tracks']]
            else:
                break
