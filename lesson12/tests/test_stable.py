import pytest


@pytest.mark.smoke
def test_health(api):
    assert api.get(api.base + "/api/health", timeout=5).status_code == 200


@pytest.mark.parametrize("age, expected", [(0, 120), (18, 150), (65, 225), (80, 225)])
def test_quote(api, age, expected):
    r = api.get(api.base + "/api/quote", params={"age": age, "days": 5}, timeout=5)
    assert r.json()["premium"] == expected


def test_create_and_delete(api, holder):
    r = api.post(api.base + "/api/policies", json={"holder": holder, "age": 30, "days": 5}, timeout=5)
    assert r.status_code == 201
    assert api.delete(api.base + f"/api/policies/{r.json()['no']}", timeout=5).status_code == 204
