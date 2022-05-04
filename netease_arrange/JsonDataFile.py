import json
import os.path
from pathlib import Path

from .constant import constant


class JsonDataFile:
    def __init__(self, path: Path or str, default_data: dict or list) -> None:
        path = Path(path)
        self.path = path
        if os.path.getsize(self.path) == 0:
            self.data = default_data
        else:
            self.data = json.loads(self.path.read_text(encoding='utf-8'))

    def __del__(self) -> None:
        self.write()

    def write(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')


json_data_file = JsonDataFile(constant.data_path , default_data={
    "netease":
        {
            "last_recorded": [],
            "waitting_resources": [],
            "waitting_be_deleted": [],
            "last_deleted":[]
        },
    "depository":
        {
            "last_recorded": []
        }
})
