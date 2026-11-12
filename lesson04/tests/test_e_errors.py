import pytest
import requests


@pytest.mark.parametrize("payload, field", [
    pytest.param({"age": 30, "days": 5}, "holder", id="缺少holder"),
    pytest.param({"holder": "", "age": 30, "days": 5}, "holder", id="holder空白"),
    pytest.param({"holder": "王小明", "age": "30", "days": 5}, "age", id="age是字串"),
    pytest.param({"holder": "王小明", "age": 81, "days": 5}, "age", id="超過承保上限"),
    pytest.param({"holder": "王小明", "age": 30, "days": 0}, "days", id="天數為零"),
])
def test_create_policy_validation(api, payload, field):
    before = api.get("/api/policies").json()["total"]

    r = api.post("/api/policies", json=payload)

    assert r.status_code == 422
    assert r.json()["field"] == field
    assert api.get("/api/policies").json()["total"] == before     # 沒有多出資料


def test_broken_json(api):
    r = api.post("/api/policies", data="{holder: 王小明",
                 headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert r.json()["error"] == "JSON 格式錯誤"


def test_policy_not_found(api):
    r = api.get("/api/policies/TP999999")
    assert r.status_code == 404
    assert "TP999999" in r.json()["error"]


def test_method_not_allowed(api):
    r = api.request("PUT", "/api/quote")
    assert r.status_code == 405
    assert r.headers["Allow"] == "GET"


def test_timeout(anon):
    with pytest.raises(requests.exceptions.Timeout):
        anon.get("/api/slow", params={"seconds": 2}, timeout=0.5)


def test_connection_refused():
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get("http://127.0.0.1:9/api/health", timeout=2)
