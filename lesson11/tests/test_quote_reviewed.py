import pytest


@pytest.mark.smoke
def test_quote_adult(api):
    r = api.get(api.base + "/api/quote", params={"age": 30, "days": 5}, timeout=5)

    assert r.status_code == 200
    assert r.json() == {"premium": 150, "currency": "TWD"}


@pytest.mark.regression
@pytest.mark.parametrize("age, expected", [
    pytest.param(0, 120, id="0歲-承保下限"),
    pytest.param(17, 120, id="17歲-未成年上限"),
    pytest.param(18, 150, id="18歲-成年下限"),
    pytest.param(64, 150, id="64歲-成年上限"),
    pytest.param(65, 225, id="65歲-高齡下限"),
    pytest.param(80, 225, id="80歲-承保上限"),
])
def test_quote_age_bands(api, age, expected):
    r = api.get(api.base + "/api/quote", params={"age": age, "days": 5}, timeout=5)

    assert r.json()["premium"] == expected, f"保費不符：{age} 歲預期 {expected}，實際 {r.json()['premium']}"


@pytest.mark.regression
def test_create_policy(api, holder):
    r = api.post(api.base + "/api/policies", json={"holder": holder, "age": 30, "days": 5}, timeout=5)
    try:
        assert r.status_code == 201, r.text
        assert r.json()["no"].startswith("TP")
        assert r.json()["premium"] == 150
    finally:
        if r.status_code == 201:
            api.delete(api.base + f"/api/policies/{r.json()['no']}", timeout=5)
