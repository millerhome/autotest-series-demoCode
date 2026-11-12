import os
import threading
from urllib.parse import urlparse

import pytest
from zeep import Client
from zeep.transports import Transport

from policy_ws import PATH, make_server

ALLOWED_HOSTS = {"127.0.0.1", "localhost", "sit.example.test"}     # 允許執行測試的主機


@pytest.fixture(scope="session")
def ws_url():
    """受測 Web Service 的網址。有設定 TEST_WS_URL 就用它，否則啟動本機的練習服務。"""
    url = os.environ.get("TEST_WS_URL")
    if url:
        host = urlparse(url).hostname
        if host not in ALLOWED_HOSTS:
            pytest.exit(f"拒絕執行：{host} 不在測試主機白名單內", returncode=2)
        yield url
        return
    server = make_server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}{PATH}"
    server.shutdown()


def make_client(ws_url):
    transport = Transport(timeout=10, operation_timeout=10)     # 讀 WSDL 與呼叫操作的逾時
    return Client(ws_url + "?WSDL", transport=transport)


@pytest.fixture(scope="session")
def client(ws_url):
    """已經登入的 zeep Client，整個測試過程只讀一次 WSDL、只登入一次。"""
    c = make_client(ws_url)
    token = c.service.Login(username=os.environ.get("TEST_USER", "tester"),
                            password=os.environ.get("TEST_PASSWORD", "test-pass-123"))
    header = c.get_element("ns0:AuthHeader")(Token=token)
    c.set_default_soapheaders([header])            # 之後每一次呼叫都帶著這個 SOAP Header
    return c


@pytest.fixture(scope="session")
def ws(client):
    """已經登入的服務代理：ws.操作名稱(參數) 就是一次 SOAP 呼叫。"""
    return client.service


@pytest.fixture(scope="session")
def anon(ws_url):
    """沒有登入的服務代理。"""
    return make_client(ws_url).service


@pytest.fixture
def policy(ws):
    """建立一張保單給測試使用，測試結束後註銷。"""
    p = ws.CreatePolicy(holder="王小明", age=30, days=5)
    yield p
    if ws.GetPolicy(policyNo=p.PolicyNo).Status == "active":
        ws.CancelPolicy(policyNo=p.PolicyNo)
