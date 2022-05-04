from typing import List, Dict, Optional

from .Paths import paths
from .raw_api import RawApi
from .util import DataDict, diff_dict


class Api:

    def __init__(self, account: str, password: str) -> None:
        self.data = DataDict(paths['api_data'], dict(), 'utf-8', False)
        self.data.read()
        if self._login(account, password):
            self.data.update(self._merge_playlists(self.data, *self.get_playlists()))
            self.data.write()

    def _login(self, account: str, password: str) -> bool:
        if r := RawApi.login(account, password):
            self.user_id = r.json()['account']['id']
            return True
        return False

    def get_playlists(self) -> (bool, Dict[str, List]):
        playlists = dict()
        finished = True
        if r := RawApi.get_playlists(self.user_id):
            for playlist in r.json()['playlist']:
                if (songs := self.get_songs_from_playlist(playlist['id'])) is not None:
                    playlists[playlist['name']] = songs
                else:
                    finished = False
                    break
        return finished, playlists

    def get_songs_from_playlist(self, playlist_id: int) -> Optional[List[Dict]]:
        songs = list()
        if r := RawApi.get_songs_from_playlist(playlist_id):
            for song in r.json()['playlist']['tracks']:
                song_ = dict(
                    name=song['name'],
                    id=song['id'],
                    artists=[
                        dict(
                            name=artist['name'],
                            id=artist['id']
                        ) for artist in song['ar']
                    ]
                )
                songs.append(song_)
            return songs

    @staticmethod
    def _merge_playlists(playlists_before: Dict, finished: bool, playlists_now: Dict) -> Dict:

        diff = diff_dict(playlists_before, playlists_now)
        for key in diff['+']:
            playlists_before[key] = list()
        if finished:
            for key in diff['-']:
                del playlists_before[key]

        for playlist_name, songs in playlists_now.items():
            playlists_before[playlist_name] = playlists_now[playlist_name]

        return playlists_before
