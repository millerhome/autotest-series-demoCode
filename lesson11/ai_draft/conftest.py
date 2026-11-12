import threading
import uuid

import pytest
import requests

from policy_api import make_server


@pytest.fixture(scope="session")
def base_url():
    server = make_server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def api(base_url):
    s = requests.Session()
    r = s.post(base_url + "/api/login", json={"username": "tester", "password": "test-pass-123"}, timeout=5)
    s.headers["Authorization"] = f"Bearer {r.json()['token']}"
    s.base = base_url
    return s


@pytest.fixture
def holder():
    return f"測試_{uuid.uuid4().hex[:6]}"
