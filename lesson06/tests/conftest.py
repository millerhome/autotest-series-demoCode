import os
import threading
import uuid

import pytest
import requests

from policy_db import connect
from policy_service import make_server
from testdata import delete_test_data, fake_customer


@pytest.fixture(scope="session")
def run_id():
    """這一次執行的代號，放進測試資料的姓名裡。"""
    return uuid.uuid4().hex[:6]


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    """資料庫的位置。有設定 TEST_DB_PATH 就用它，否則建立一個暫時的資料庫。"""
    return os.environ.get("TEST_DB_PATH") or str(tmp_path_factory.mktemp("db") / "test.db")


@pytest.fixture(scope="session")
def base_url(db_path):
    server = make_server(db_path)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def api(base_url):
    """很小的 API client：只記住網址與逾時。"""
    session = requests.Session()

    def call(method, path, **kwargs):
        kwargs.setdefault("timeout", 5)
        return session.request(method, base_url + path, **kwargs)

    yield call
    session.close()


@pytest.fixture
def db(db_path, base_url):
    """給測試用的資料庫連線（唯讀用途為主），測試結束後關閉。"""
    conn = connect(db_path)
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def sweep_test_data(db_path, base_url, run_id):
    """整個測試結束後，把這一次執行留下的測試資料清掉。"""
    yield
    conn = connect(db_path)
    delete_test_data(conn, f"測試_{run_id}_%")
    conn.close()


@pytest.fixture
def customer_data(run_id):
    """一筆還沒有寫進資料庫的假客戶資料，給「透過 API 建立」的測試使用。"""
    return fake_customer(run_id)


@pytest.fixture
def make_policy(db, run_id):
    """工廠 fixture：直接在資料庫建立一張指定狀態的保單，回傳保單號碼。"""
    def _make(status="active", age=30, days=5, premium=150, created_at="2026-01-01T00:00:00+00:00"):
        c = fake_customer(run_id)
        cur = db.execute("INSERT INTO customers (name, id_no, phone) VALUES (:name, :id_no, :phone)", c)
        cur = db.execute("INSERT INTO policies (customer_id, age, days, premium, status, created_at)"
                         " VALUES (?, ?, ?, ?, ?, ?)",
                         (cur.lastrowid, age, days, premium, status, created_at))
        policy_no = f"TP{cur.lastrowid:06d}"
        db.execute("UPDATE policies SET policy_no = ? WHERE policy_id = ?", (policy_no, cur.lastrowid))
        db.commit()
        return policy_no
    return _make
