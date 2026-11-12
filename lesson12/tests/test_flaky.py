"""不穩定測試的兩個典型：時間太緊、依賴其他測試的資料。"""
import pytest

_created = {}


@pytest.mark.quarantine(reason="服務偶爾回應超過 0.5 秒，逾時設得太緊", ticket="TFS#5120")
def test_quote_fast(api):
    """逾時設得太緊：服務偶爾變慢 0.6 秒，就會失敗。"""
    r = api.get(api.base + "/api/quote", params={"age": 30, "days": 5}, timeout=0.5)
    assert r.json()["premium"] == 150


def test_a_create_shared(api):
    r = api.post(api.base + "/api/policies", json={"holder": "共用資料", "age": 30, "days": 5}, timeout=5)
    _created["no"] = r.json()["no"]


@pytest.mark.quarantine(reason="依賴 test_a 建立的資料，單獨執行會失敗", ticket="TFS#5121")
def test_b_read_shared(api):
    """依賴上一支測試建立的資料：單獨執行或換順序就會失敗。"""
    r = api.get(api.base + f"/api/policies/{_created['no']}", timeout=5)
    assert r.status_code == 200
