from .constant import BASE_PATH, COOKIES_PATH, API_DATA_PATH, DATA_PATH

if not BASE_PATH.exists():
    BASE_PATH.mkdir()
if not COOKIES_PATH.exists():
    COOKIES_PATH.write_text('#LWP-Cookies-2.0\n')
if not API_DATA_PATH.exists():
    API_DATA_PATH.touch()
if not DATA_PATH.exists():
    DATA_PATH.touch()

from .Depository import Depository
from .LocalSong import LocalSong, MusicNameFormat
from .Netease import Netease

from .JsonDataFile import JsonDataFile
