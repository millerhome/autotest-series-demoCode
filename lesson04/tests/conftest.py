import os
import threading
from urllib.parse import urlparse

import pytest
from api_client import ApiClient
from policy_api import make_server

ALLOWED_HOSTS = {"127.0.0.1", "localhost", "sit.example.test"}     # 允許執行測試的主機


@pytest.fixture(scope="session")
def base_url():
    """受測服務的網址。有設定 TEST_BASE_URL 就用它，否則啟動本機的練習服務。"""
    url = os.environ.get("TEST_BASE_URL")
    if url:
        host = urlparse(url).hostname
        if host not in ALLOWED_HOSTS:
            pytest.exit(f"拒絕執行：{host} 不在測試主機白名單內", returncode=2)
        yield url.rstrip("/")
        return
    server = make_server()          # port=0：由系統挑一個空的埠
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def anon(base_url):
    """沒有登入的 client。"""
    client = ApiClient(base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def api(base_url):
    """已經登入的 client，整個測試過程只登入一次。"""
    client = ApiClient(base_url)
    client.login(os.environ.get("TEST_USER", "tester"),
                 os.environ.get("TEST_PASSWORD", "test-pass-123"))
    yield client
    client.close()


@pytest.fixture
def policy(api):
    """建立一張保單給測試使用，測試結束後刪除。"""
    r = api.post("/api/policies", json={"holder": "王小明", "age": 30, "days": 5})
    assert r.status_code == 201, r.text
    data = r.json()
    yield data
    api.delete(f"/api/policies/{data['no']}")
