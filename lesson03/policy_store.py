"""教學用的保單庫：資料存在一個 JSON 檔裡。"""
import json
from pathlib import Path


class PolicyStore:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, no, holder, premium):
        data = self._load()
        if no in data:
            raise KeyError(f"保單號碼重複：{no}")
        data[no] = {"holder": holder, "premium": premium}
        self.path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def get(self, no):
        return self._load().get(no)

    def count(self):
        return len(self._load())
