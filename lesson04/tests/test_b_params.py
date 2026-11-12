import pytest


@pytest.mark.parametrize("age, expected", [
    pytest.param(0, 120, id="0歲-承保下限"),
    pytest.param(17, 120, id="17歲-未成年上限"),
    pytest.param(18, 150, id="18歲-成年下限"),
    pytest.param(64, 150, id="64歲-成年上限"),
    pytest.param(65, 225, id="65歲-高齡下限"),
    pytest.param(80, 225, id="80歲-承保上限"),
])
def test_quote_age_bands(anon, age, expected):
    r = anon.get("/api/quote", params={"age": age, "days": 5})
    assert r.status_code == 200
    assert r.json()["premium"] == expected


@pytest.mark.parametrize("params, field", [
    pytest.param({"age": -1, "days": 5}, "age", id="年齡為負"),
    pytest.param({"age": 81, "days": 5}, "age", id="超過承保上限"),
    pytest.param({"age": 30, "days": 0}, "days", id="天數為零"),
])
def test_quote_rejects_invalid(anon, params, field):
    r = anon.get("/api/quote", params=params)
    assert r.status_code == 422
    assert r.json()["field"] == field


@pytest.mark.parametrize("params", [
    pytest.param({"days": 5}, id="缺少age"),
    pytest.param({"age": "abc", "days": 5}, id="age不是數字"),
])
def test_quote_bad_params(anon, params):
    r = anon.get("/api/quote", params=params)
    assert r.status_code == 422
    assert "error" in r.json()
