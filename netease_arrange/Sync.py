def Sync(account: str,
         password: str,
         depository: str,
         netease_download_path: str
         ):
    from .constant import constant
    constant.init(account)
    from .Netease import Netease
    netease = Netease(netease_download_path, account, password)
    from .Depository import Depository
    depository = Depository(depository)
    depository.diff()
    netease.sync(depository)