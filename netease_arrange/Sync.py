def Sync(account: str or int,
         password: str or int,
         depository: str,
         netease_download_path: str
         ):
    account = str(account)
    password = str(password)
    from .Paths import paths
    paths.init(account)
    from .Netease import Netease
    netease = Netease(netease_download_path, account, password)
    from .Depository import Depository
    depository = Depository(depository)
    depository.diff()
    netease.sync(depository)
    from .Record import record
    record.write()
