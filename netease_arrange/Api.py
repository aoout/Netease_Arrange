'''
make the acquired data more structured and try to reduce the inconvenience of access restrictions.
'''

# pylint:disable = line-too-long,invalid-name

from typing import Dict, Optional, Tuple

from .Paths import paths
from .raw_api import RawApi
from .util import DataDict, to_pathname


class Api:
    '''
    make the acquired data more structured and try to reduce the inconvenience of access restrictions.
    '''

    def __init__(self, account: str, password: str) -> None:
        self.account = account
        self.password = password
        self.user_id = RawApi.login_cellphone(self.account, self.password)
        self.data = DataDict(
            paths['api_data'], encoding='utf-8', ensure_ascii=False)
        self.data.read()
        self.playlist_filter = lambda playlist: not playlist['subscribed']

    def update(self) -> None:
        '''
        like NetEase Cloud Music sends a request to update
        the data of the persistently stored playlist data dictionary.
        '''
        playlists_keys, finished_part = self.request_result()

        for key in self.data.copy().keys():
            if key not in playlists_keys:
                del self.data[key]

        self.data.update(finished_part)

        self.data.write()

    def request_result(self) -> Tuple[list, dict]:
        '''
        returns the names of all playlists,
        and a data dictionary containing those playlists that have completed data acquisition.
        '''
        finished_part = {}
        playlists = self.playlists()
        for playlist in playlists.values():
            if songs := self.songs(playlist):
                finished_part[playlist['name']] = songs
            else:
                break
        return playlists.keys(), finished_part

    def playlists(self) -> Dict:
        '''
        get the data dictionary of the user's playlist,
        which does not contain data for songs in the playlist.
        '''
        playlists = {}
        raw_playlists = RawApi.user_playlist(self.user_id)
        for raw_playlist in raw_playlists:
            playlist = dict(
                name=raw_playlist['name'],
                id=raw_playlist['id'],
                subscribed=raw_playlist['subscribed'],
                tags=raw_playlist['tags'],
                songs=[]
            )
            if self.playlist_filter(playlist):
                playlists[playlist['name']] = playlist
        return playlists

    def songs(self, playlist: Dict) -> Optional[Dict]:
        '''
        get the data dictionary of the songs in a certain playlist of the user,
        which does not contain the download link.
        if the access limit is reached, a null value will be returned.
        '''
        songs = {}
        # there may be a null value here because the access limit is reached.
        if playlist_detail := RawApi.playlist_detail(playlist['id']):
            songs_id = [song_['id'] for song_ in playlist_detail]
            # there may be a null value here because the access limit is reached.
            if raw_songs := RawApi.song_detail_unlimited(songs_id):
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
        return None
