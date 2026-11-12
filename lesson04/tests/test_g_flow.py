import pytest


@pytest.mark.regression
def test_policy_lifecycle(api):
    # 1. 先試算
    r = api.get("/api/quote", params={"age": 70, "days": 10})
    assert r.status_code == 200
    quoted = r.json()["premium"]

    # 2. 投保，保費要跟試算一致
    r = api.post("/api/policies", json={"holder": "陳小華", "age": 70, "days": 10})
    assert r.status_code == 201, r.text
    no = r.json()["no"]
    assert r.json()["premium"] == quoted

    # 3. 查得到
    r = api.get(f"/api/policies/{no}")
    assert r.status_code == 200
    assert r.json()["holder"] == "陳小華"

    # 4. 刪除
    assert api.delete(f"/api/policies/{no}").status_code == 204

    # 5. 再查就找不到
    assert api.get(f"/api/policies/{no}").status_code == 404
