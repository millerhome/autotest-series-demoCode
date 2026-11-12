"""修好之後的版本：放回正常的測試裡。"""


def test_quote_normal_timeout(api):
    r = api.get(api.base + "/api/quote", params={"age": 30, "days": 5}, timeout=5)
    assert r.json()["premium"] == 150


def test_read_own_policy(api, holder):
    r = api.post(api.base + "/api/policies", json={"holder": holder, "age": 30, "days": 5}, timeout=5)
    no = r.json()["no"]
    try:
        assert api.get(api.base + f"/api/policies/{no}", timeout=5).status_code == 200
    finally:
        api.delete(api.base + f"/api/policies/{no}", timeout=5)
