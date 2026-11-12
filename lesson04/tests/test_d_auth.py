import pytest


def test_login_success(anon):
    r = anon.post("/api/login", json={"username": "tester", "password": "test-pass-123"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "Bearer"
    assert len(body["token"]) == 32


def test_login_wrong_password(anon):
    r = anon.post("/api/login", json={"username": "tester", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["error"] == "帳號或密碼錯誤"


@pytest.mark.parametrize("headers", [
    pytest.param({}, id="沒有帶token"),
    pytest.param({"Authorization": "Bearer not-a-real-token"}, id="token無效"),
    pytest.param({"Authorization": "Basic abc"}, id="驗證方式錯誤"),
])
def test_policies_require_token(anon, headers):
    r = anon.get("/api/policies", headers=headers)
    assert r.status_code == 401
    assert r.headers["WWW-Authenticate"] == "Bearer"
