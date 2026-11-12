import pytest


@pytest.mark.smoke
def test_create_policy(api):
    payload = {"holder": "林小美", "age": 30, "days": 5}

    r = api.post("/api/policies", json=payload)

    assert r.status_code == 201
    body = r.json()
    assert body["holder"] == "林小美"
    assert body["premium"] == 150
    assert body["status"] == "active"
    assert r.headers["Location"] == f"/api/policies/{body['no']}"

    api.delete(f"/api/policies/{body['no']}")      # 清理（下一章改用 fixture）


def test_created_policy_can_be_read(api, policy):
    r = api.get(f"/api/policies/{policy['no']}")
    assert r.status_code == 200
    assert r.json() == policy


def test_delete_policy(api, policy):
    r = api.delete(f"/api/policies/{policy['no']}")
    assert r.status_code == 204
    assert r.text == ""

    r = api.get(f"/api/policies/{policy['no']}")
    assert r.status_code == 404


def test_search_by_holder(api, policy):
    r = api.get("/api/policies", params={"holder": "王小明"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert policy["no"] in [p["no"] for p in body["items"]]
