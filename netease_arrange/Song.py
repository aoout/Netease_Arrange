from abc import ABCMeta
from collections import UserList
from typing import List


class Song(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.name = None

    def __repr__(self) -> None:
        return f'{self.__class__.__name__}:{self.name}'

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class NoTheSongError(Exception):
    # todo:添加详细的错误信息
    pass


class Songs(UserList):
    def __init__(self) -> None:
        super().__init__()

    def __getitem__(self, name: str) -> Song:
        # todo:如果有重名歌曲怎么办，或许可以添加歌手信息来识别
        if len((results := [song for song in self.data if song.name == name])) == 1:
            return results[0]
        else:
            raise NoTheSongError()

    @property
    def names(self) -> List[str]:
        return [song.name for song in self.data]
