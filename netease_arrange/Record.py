from .Paths import paths

from .util import DataDict


class Record(DataDict):
    def __init__(self):
        super().__init__(path=paths['data'],
                         default_value=dict(
                             netease=dict(
                                 old=list(),
                                 unavailable=list(),
                                 deleting=list(),
                                 last_deleted=list(),
                                 invalid = list()
                             ),
                             depository=dict(
                                 old=list()
                             )
                         ),
                         encoding='utf-8',
                         ensure_ascii=False)


record = Record()
