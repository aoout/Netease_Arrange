from typing import Callable, Optional,List


def Sync(account: str or int,
         password: str or int,
         depository: str,
         netease_download_path: str,
         playlist_filter: Optional[Callable]=None,
         folders_prefix:List[str]=list()
         ):
    account = str(account)
    password = str(password)
    from .Paths import paths
    paths.init(account)

    from .Netease import Netease
    netease = Netease(netease_download_path, folders_prefix)
    netease.login(account,password)
    if playlist_filter:
        netease.api.playlist_filter = playlist_filter

    from .Depository import Depository
    depository = Depository(depository)
    depository.diff()
    netease.sync(depository)

    from .Record import record
    record.write()
