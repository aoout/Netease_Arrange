from typing import Dict, Optional,Tuple

from .Paths import paths
from .raw_api import RawApi
from .util import DataDict, diff_dict, to_pathname


class Api:

    def __init__(self, account: str, password: str) -> None:
        self.account = account
        self.password = password
        self.data = DataDict(paths['api_data'], dict(), 'utf-8', False)
        self.data.read()
        self.playlist_filter = lambda playlist: True if playlist['subscribed'] == False else False

    def update(self) -> None:
        self.user_id = RawApi.login_cellphone(self.account, self.password)
        self.data.update(self.merge_playlists(self.data, *self.request_result(self.user_id)))
        self.data.write()

    def request_result(self, user_id: int) -> Tuple[list, dict]:
        finished_part = dict()
        playlists = self.playlists(user_id)
        for playlist in playlists.values():
            if songs := self.songs(playlist):
                finished_part[playlist['name']] = songs
            else:
                break
        return playlists.keys(), finished_part 

    def playlists(self, user_id: int) -> Dict:
        '''该方法没有调用受到限制的请求'''
        playlists = dict()
        raw_playlists = RawApi.user_playlist(user_id)
        for raw_playlist in raw_playlists:
            playlist = dict(
                name=raw_playlist['name'],
                id=raw_playlist['id'],
                subscribed=raw_playlist['subscribed'],
                tags=raw_playlist['tags'],
                songs=list()
            )
            if self.playlist_filter(playlist):
                playlists[playlist['name']] = playlist
        return playlists

    def songs(self, playlist: Dict) -> Optional[Dict]:
        '''该方法调用了受到限制的请求'''
        songs = dict()
        if playlist_detail := RawApi.playlist_detail(playlist['id']):
            songs_id = [song_['id'] for song_ in playlist_detail]
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
                    songs[song['name']] = song
                print(f'the data about {playlist["name"]} have updated.')
                return songs

    @staticmethod
    def merge_playlists(playlists_before: Dict, playlists_name: list, finished_part: dict) -> Dict:

        diff = diff_dict(playlists_before, finished_part)
        for key in diff['+']:
            playlists_before[key] = list()

        for key in playlists_before.copy().keys():
            if key not in playlists_name:
                del playlists_before[key]


        for playlist_name, songs in finished_part.items():
            playlists_before[playlist_name] = finished_part[playlist_name]

        return playlists_before
