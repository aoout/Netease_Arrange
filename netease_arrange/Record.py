# pylint:disable = missing-module-docstring,invalid-name
from .Paths import Paths

from .util import DataDict, Singleton

@Singleton
class Record(DataDict):
    '''
    storage some information about the song file management.
    '''

    def __init__(self):
        super().__init__(path=Paths()['data'],
                         default_value=dict(
                             netease=dict(
                                 old=[],
                                 unavailable=[],
                                 deleting=[],
                                 last_deleted=[],
                                 invalid=[]
                             ),
                             depository=dict(
                                 old=[]
                             )
        ),
            encoding='utf-8',
            ensure_ascii=False)
