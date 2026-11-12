import pytest
import requests


@pytest.mark.smoke
def test_health(base_url):
    r = requests.get(f"{base_url}/api/health", timeout=5)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_quote_adult(base_url):
    r = requests.get(f"{base_url}/api/quote",
                     params={"age": 30, "days": 5}, timeout=5)

    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    assert r.json() == {"premium": 150, "currency": "TWD"}


def test_response_time(base_url):
    r = requests.get(f"{base_url}/api/health", timeout=5)
    assert r.elapsed.total_seconds() < 1
