import random
from typing import List, Dict

from .Paths import paths
from .raw_api import RawApi
from .util import DataDict, diff_dict, to_pathname


class Api:

    def __init__(self, account: str, password: str) -> None:
        self.data = DataDict(paths['api_data'], dict(), 'utf-8', False)
        self.data.read()
        self.data.update(self._merge_playlists(self.data, *self._playlists(RawApi.login_cellphone(account, password))))
        self.data.write()

    def _playlists(self, user_id: int) -> (bool, Dict[str, List]):
        finished = True
        playlists = dict()
        raw_user_playlist = RawApi.user_playlist(user_id)
        random.shuffle(raw_user_playlist)
        for raw_playlist in raw_user_playlist:
            songs = list()
            if playlist_detail := RawApi.playlist_detail(raw_playlist['id']):
                songs_id = [x['id'] for x in playlist_detail]
                if raw_songs := RawApi.song_detail_h(songs_id):
                    for raw_song in raw_songs:
                        song = dict(
                            name=to_pathname(raw_song['name']),
                            id=raw_song['id'],
                            artists=[dict(
                                name=artist['name'],
                                id=artist['id']
                            ) for artist in raw_song['ar']]
                        )
                        songs.append(song)
                    print(f'the data about {raw_playlist["name"]} have updated.')
                else:
                    return False, playlists

            else:
                finished = False
                break
            playlists[to_pathname(raw_playlist['name'])] = songs
        return finished, playlists

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
