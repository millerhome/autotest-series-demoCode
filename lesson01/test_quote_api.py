import pytest
import requests


@pytest.mark.smoke
def test_quote_returns_premium(base_url):
    r = requests.get(f"{base_url}/api/quote", params={"age": 30, "days": 5}, timeout=5)

    assert r.status_code == 200
    assert r.json() == {"premium": 150, "currency": "TWD"}


@pytest.mark.regression
def test_senior_gets_higher_premium(base_url):
    r = requests.get(f"{base_url}/api/quote", params={"age": 65, "days": 5}, timeout=5)

    assert r.json()["premium"] == 225


@pytest.mark.regression
def test_out_of_range_age_is_422(base_url):
    r = requests.get(f"{base_url}/api/quote", params={"age": 81, "days": 5}, timeout=5)

    assert r.status_code == 422
    assert "承保範圍" in r.json()["error"]
