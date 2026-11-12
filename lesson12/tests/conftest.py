import threading
import uuid

import pytest
import requests

from policy_api import make_server


def pytest_addoption(parser):
    parser.addoption("--run-quarantine", action="store_true", help="也執行被隔離的測試")


def pytest_collection_modifyitems(config, items):
    """被隔離的測試，平常不執行；需要時加上 --run-quarantine。"""
    if config.getoption("--run-quarantine"):
        return
    keep, quarantined = [], []
    for item in items:
        (quarantined if item.get_closest_marker("quarantine") else keep).append(item)
    if quarantined:
        config.hook.pytest_deselected(items=quarantined)
        items[:] = keep
        config._quarantined = quarantined


def pytest_terminal_summary(terminalreporter, config):
    """在結尾列出被隔離的測試，提醒大家它們還沒修好。"""
    for item in getattr(config, "_quarantined", []):
        m = item.get_closest_marker("quarantine")
        terminalreporter.write_line(f"隔離中：{item.nodeid}｜{m.kwargs.get('reason')}｜{m.kwargs.get('ticket')}")


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
