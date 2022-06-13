'''
log in to NetEase Cloud Music and send various requests.
'''
# pylint:disable = line-too-long

import json
import platform
from http.cookiejar import Cookie, LWPCookieJar
from typing import Callable, List, Optional

import requests
from requests.models import Response

from ..Paths import Paths
from ..util import is_json
from .decrypt import encrypted_password, encrypted_request

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": 'gzip,deflate,sdch',
    "Accept-Language": "zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "music.163.com",
    "Referer": "http://music.163.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/88.0.4324.87 Safari/537.36",
}


class RawApi:
    '''
    log in to NetEase Cloud Music and send various requests.
    each function that sends a request sets the hook parameter to process the obtained response.
    these hooks are set to default values to get the most useful parts in general.
    except for the "user_playlist" method, the requests sent by other methods that send requests seem to be limited by the frequency of access.
    '''

    @classmethod
    def geturl(cls, path: str) -> str:
        '''
        get requested url from path.
        '''
        return 'http://music.163.com/weapi/' + path

    @classmethod
    def login_cellphone(cls, account: str, password: str,
                        hook: Optional[Callable] = lambda response: response.json()['account']['id']):
        '''
        log in to NetEase Cloud account with mobile phone number and password.
        '''
        hook = hook if hook else lambda _:_

        RawApi._init_session()

        user_info = dict(phone=account, password=encrypted_password(password))
        params = dict(user_info, coutrycode='86', rememberLogin='true')
        response = cls._request('post', RawApi.geturl(
            'login/cellphone'), params, {"os": "pc"})
        cls._session.cookies.save()
        return hook(response) if RawApi._response_vaild(response) else None

    @classmethod
    def _init_session(cls) -> None:
        '''
        initialize sessions needed on subsequent requests, load cookies stored in files.
        '''

        cls._session = requests.Session()

        cookie_jar = LWPCookieJar(Paths()['cookies'])
        cookie_jar.load()

        cls._session.cookies = cookie_jar
        for cookie in cookie_jar:
            if cookie.is_expired():
                cookie_jar.clear()
                break

    @classmethod
    def user_playlist(cls, user_id: str,
                      hook: Optional[Callable] = lambda response: response.json()['playlist']):
        '''
        get all the user's playlists.
        '''
        hook = hook if hook else lambda _:_ 
        params = dict(uid=user_id, offset=0, limit=50)
        response = cls._request('post', RawApi.geturl('user/playlist'), params)
        return hook(response) if RawApi._response_vaild(response) else None

    @classmethod
    def playlist_detail(cls, playlist_id: int,
                        hook: Optional[Callable] = lambda response: response.json()['playlist']['trackIds']):
        '''
        get more detailed information through the id value of a playlist.
        '''
        hook = hook if hook else lambda _:_ 
        params = dict(id=playlist_id, total='true',
                      limit=1000, n=1000, offset=0)
        response = cls._request('post', RawApi.geturl(
            'v3/playlist/detail'), params, dict(os=platform.system()))
        return hook(response) if RawApi._response_vaild(response) else None

    @classmethod
    def song_detail(cls, songs_id: List[int],
                    hook: Optional[Callable] = lambda response: response.json()['songs']):
        '''
        get more detailed information through the ids value of songs.
        only a maximum of 1000 ids can be passed in at a time.
        '''
        hook = hook if hook else lambda _:_ 
        params = dict(c=json.dumps([{"id": _id}
                      for _id in songs_id]), ids=json.dumps(songs_id))
        response = cls._request(
            'post', RawApi.geturl('v3/song/detail'), params)
        return hook(response) if RawApi._response_vaild(response) else None

    @classmethod
    def song_detail_unlimited(cls, songs_id: List[int],
                              hook: Optional[Callable] = lambda response: response.json()['songs']):
        '''
        get more detailed information through the ids value of songs.
        an unlimited number of ids can be passed in.
        '''
        hook = hook if hook else lambda _:_ 
        result = []
        while len(songs_id)>1000:
            result.extend(RawApi.song_detail(songs_id[0:1000]))
            del songs_id[0:1000]
        result.extend(RawApi.song_detail(songs_id))
        return result


    @classmethod
    def _request(cls, method: str, url: str, params: dict, custom_cookies: Optional[dict] = None) -> Response:
        '''
        send request. will encrypt parameters and modify some cookie values.
        '''
        custom_cookies = custom_cookies if custom_cookies else {}
        csrf_token = ""
        for cookie in cls._session.cookies:
            if cookie.name == "__csrf":
                csrf_token = cookie.value
                break
        params.update({"csrf_token": csrf_token})
        for key, value in custom_cookies.items():
            cookie = cls._make_cookie(key, value)
            cls._session.cookies.set_cookie(cookie)

        if method == 'get':  # pylint:disable = no-else-return
            return cls._session.request(method=method, url=url, headers=HEADERS, params=encrypted_request(params))
        elif method == 'post':
            return cls._session.request(method=method, url=url, headers=HEADERS, data=encrypted_request(params))
        else:
            raise Exception('Incorrect parameter entered')

    @classmethod
    def _make_cookie(cls, name: str, value: str) -> Cookie:
        return Cookie(
            version=0, name=name, value=value, port=None, port_specified=False, domain="music.163.com",
            domain_specified=True, domain_initial_dot=False, path="/", path_specified=True, secure=False,
            expires=None, discard=False, comment=None, comment_url=None, rest={},
        )

    @staticmethod
    def _response_vaild(response: Response) -> bool:
        '''
        retermine whether the received response is valid.
        '''
        if response.status_code == 200:
            if is_json(response.text):
                if 'code' not in response.json() or response.json()['code'] == 200:
                    return True
        print(f'the request to {response.url} failed.')
        print(f'{response.text}')
        return False
