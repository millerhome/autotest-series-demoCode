import re
from datetime import datetime


def test_dynamic_fields(policy):
    # 會變動的欄位：只驗證格式
    assert re.fullmatch(r"TP\d{6}", policy["no"])
    datetime.fromisoformat(policy["created_at"])      # 不是合法的時間就會丟出例外

    # 其他欄位：拿掉會變動的，剩下的完整比對
    stable = {k: v for k, v in policy.items() if k not in ("no", "created_at")}
    assert stable == {"holder": "王小明", "age": 30, "days": 5,
                      "premium": 150, "currency": "TWD", "status": "active"}
