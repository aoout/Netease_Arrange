from enum import Enum
from pathlib import Path

from .Song import Song


class MusicNameFormat(Enum):
    Music_Name = 1
    Singer_Name_Music_Name = 2
    Music_Name_Singer_Name = 3


class LocalSong(Song):

    music_name_format: MusicNameFormat = MusicNameFormat.Singer_Name_Music_Name

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.name = self.path.stem.split(' - ')[1]
        if (self.music_name_format == MusicNameFormat.Singer_Name_Music_Name):
            self.name = self.path.stem.split(' - ')[1]
        elif (self.music_name_format == MusicNameFormat.Music_Name_Singer_Name):
            self.name = self.path.stem.split(' - ')[0]
        else:
            self.name = self.path.stem
