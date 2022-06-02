# pylint:disable = missing-module-docstring,invalid-name
from .Paths import paths

from .util import DataDict


class Record(DataDict):
    '''
    storage some information about the song file management.
    '''
    def __init__(self):
        super().__init__(path=paths['data'],
                         default_value=dict(
                             netease=dict(
                                 old=[],
                                 unavailable=[],
                                 deleting=[],
                                 last_deleted=[],
                                 invalid = []
                             ),
                             depository=dict(
                                 old=[]
                             )
                         ),
                         encoding='utf-8',
                         ensure_ascii=False)


record = Record() # implement singleton pattern.
