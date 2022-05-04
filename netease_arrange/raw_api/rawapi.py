import platform
from http.cookiejar import Cookie, LWPCookieJar
from typing import Optional

import requests
from requests.models import Response

from .decrypt import encrypted_password, encrypted_request
from ..constant import constant

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
BASE_URL = 'http://music.163.com/weapi/'
LOGIN_URL = BASE_URL + 'login/cellphone'
PLAYLIST_URL = BASE_URL + 'user/playlist'
SONGS_URL = BASE_URL + 'v3/playlist/detail'


class RawApi:
    """
    登陆网易云账号，从中获得该用户的歌单，某歌单中的歌曲信息等信息。
    并不提供下载其中歌曲的功能。这是因为通过这种api下载到的资源最高只有.mp3格式。
    然而，预先从官方客户端下载好后，可以再由本项目进行处理，就可以熊掌与鱼兼得。
    """

    @classmethod
    def login(cls, account: str, password: str) -> Optional[Response]:

        cookie_jar = LWPCookieJar(constant.cookies_path )
        cookie_jar.load()

        cls._session = requests.Session()

        cls._session.cookies = cookie_jar
        for cookie in cookie_jar:
            if cookie.is_expired():
                cookie_jar.clear()
                break

        user_info = dict(phone=account, password=encrypted_password(password))
        params = dict(user_info, coutrycode='86', rememberLogin='true')
        r = cls._request('post', LOGIN_URL, params, {"os": "pc"})
        cls._session.cookies.save()
        if r.status_code == 200 :
            if 'code' not in r.json() or r.json()['code'] == 200:
                return r
        print('Login request failed')
        print(f'{r.status_code}:{r.text}')
        return None

    @classmethod
    def get_playlists(cls, user_id: str) -> Optional[Response]:
        params = dict(uid=user_id, offset=0, limit=50)
        r = cls._request('post', PLAYLIST_URL, params)
        if r.status_code == 200:
            if 'code' not in r.json() or r.json()['code'] == 200:
                return r

        print('Playlists request failed')
        print(f'{r.status_code}:{r.text}')
        return None

    @classmethod
    def get_songs_from_playlist(cls, playlist_id: int) -> Optional[Response]:
        params = dict(id=playlist_id, total='true',
                      limit=1000, n=1000, offset=0)
        r = cls._request('post', SONGS_URL, params, dict(os=platform.system()))
        if r.status_code == 200:
            if 'code' not in r.json() or r.json()['code'] == 200:
                return r

        print('Songs requests failed')
        print(f'{r.status_code}:{r.text}')
        return None

    @classmethod
    def _request(cls, method: str, url: str, params: dict, custom_cookies: dict = {}) -> Response:
        csrf_token = ""
        for cookie in cls._session.cookies:
            if cookie.name == "__csrf":
                csrf_token = cookie.value
                break
        params.update({"csrf_token": csrf_token})
        for key, value in custom_cookies.items():
            cookie = cls._make_cookie(key, value)
            cls._session.cookies.set_cookie(cookie)

        if method == 'get':
            return cls._session.request(method=method, url=url, headers=HEADERS, params=encrypted_request(params))
        elif method == 'post':
            return cls._session.request(method=method, url=url, headers=HEADERS, data=encrypted_request(params))

    @classmethod
    def _make_cookie(cls, name: str, value: str) -> Cookie:
        return Cookie(
            version=0, name=name, value=value, port=None, port_specified=False, domain="music.163.com",
            domain_specified=True, domain_initial_dot=False, path="/", path_specified=True, secure=False,
            expires=None, discard=False, comment=None, comment_url=None, rest={},
        )
