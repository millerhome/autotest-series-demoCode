# 以下是「AI 常寫出來的樣子」的示範：由講師依常見問題整理，不是 Copilot 實際的輸出。
import time

import requests

from premium import calc_premium

BASE_URL = "http://127.0.0.1:8000"                      # 問題 1：網址寫死


def test_quote_returns_200(base_url):
    r = requests.get(f"{base_url}/api/quote", params={"age": 30, "days": 5})   # 問題 2：沒有 timeout
    assert r.status_code == 200                          # 問題 3：只驗狀態碼


def test_quote_premium_is_number(base_url):
    r = requests.get(f"{base_url}/api/quote", params={"age": 70, "days": 10}, timeout=5)
    assert isinstance(r.json()["premium"], int)          # 問題 3：只驗型別
    assert r.json()["premium"] > 0


def test_quote_matches_calculation(base_url):
    for age in [0, 17, 18, 64, 65, 80]:                  # 問題 4：迴圈代替 parametrize
        r = requests.get(f"{base_url}/api/quote", params={"age": age, "days": 5}, timeout=5)
        assert r.json()["premium"] == calc_premium(age, 5)   # 問題 5：用同一份程式算預期值


def test_create_policy(api, base_url):
    r = api.post(f"{base_url}/api/policies", json={"holder": "王小明", "age": 30, "days": 5}, timeout=5)
    time.sleep(1)                                        # 問題 6：固定等待
    assert r.status_code == 201
    assert r.json()["policy_number"].startswith("TP")    # 問題 7：不存在的欄位名稱
                                                         # 問題 8：沒有清理，固定的姓名
