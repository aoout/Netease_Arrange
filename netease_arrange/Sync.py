from typing import Callable, List, Optional

from .Depository import Depository
from .Netease import Netease
from .Paths import Paths
from .Record import Record


def sync(account: str,
         password: str,
         depository: str,
         netease_download_path: str,
         playlist_filter: Optional[Callable] = None,
         group_platlists_prefix: List[str] = None
         ):

    Paths().init(account)

    netease = Netease(netease_download_path, group_platlists_prefix)
    netease.login(account, password)
    if playlist_filter:
        netease.api.playlist_filter = playlist_filter

    depository = Depository(depository)
    depository.diff()
    netease.sync(depository)

    Record().write()
