"""候選流程評分：頻率、風險、穩定度越高越優先；自動化難度越高越往後。"""
from dataclasses import dataclass


@dataclass
class Flow:
    name: str
    frequency: int   # 多常要重測 1~5
    risk: int        # 出錯的影響 1~5
    stability: int   # 畫面與規則多穩定 1~5
    effort: int      # 自動化難度 1~5

    @property
    def score(self) -> float:
        return self.frequency * self.risk * self.stability / self.effort


flows = [
    Flow("旅平險報價→投保→出單", 5, 5, 4, 3),
    Flow("保費試算 Web Service",  5, 4, 5, 1),
    Flow("保全：變更受益人",      3, 4, 4, 3),
    Flow("理賠申請（需人工審核）", 2, 5, 3, 5),
    Flow("活動頁（下個月改版）",   2, 2, 1, 2),
]

for f in sorted(flows, key=lambda f: f.score, reverse=True):
    print(f"{f.score:6.1f}  {f.name}")
