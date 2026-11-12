import threading
import uuid

import pytest
from playwright.sync_api import Page, expect

from policy_web import make_server


@pytest.fixture(scope="session")
def base_url():
    """練習網站的網址。pytest-playwright 會把它設成瀏覽器的 base URL，所以 goto 可以只寫路徑。"""
    server = make_server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """每一支測試的瀏覽器環境：固定視窗大小與語系。"""
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}, "locale": "zh-TW"}


@pytest.fixture
def login(page: Page):
    """用畫面登入，停在保費試算頁。"""
    page.goto("/login")
    page.get_by_label("帳號").fill("tester")
    page.get_by_label("密碼").fill("test-pass-123")
    page.get_by_role("button", name="登入").click()
    expect(page.get_by_role("heading", name="保費試算")).to_be_visible()
    return page


@pytest.fixture
def holder():
    """這支測試專用的要保人姓名，不會跟別的測試重複。"""
    return f"測試_{uuid.uuid4().hex[:6]}"


@pytest.fixture
def make_policy(login: Page):
    """用 API 建立保單（共用瀏覽器的登入狀態），回傳保單資料。"""
    def _make(holder, age=30, days=5):
        r = login.request.post("/api/policies", data={"holder": holder, "age": age, "days": days})
        assert r.status == 201, r.text()
        return r.json()
    return _make


@pytest.fixture(scope="session")
def auth_state(browser, base_url, tmp_path_factory):
    """登入一次，把登入狀態（cookie）存成檔案，給後面的測試重複使用。"""
    path = tmp_path_factory.mktemp("auth") / "state.json"
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.goto("/login")
    page.get_by_label("帳號").fill("tester")
    page.get_by_label("密碼").fill("test-pass-123")
    page.get_by_role("button", name="登入").click()
    expect(page.get_by_role("heading", name="保費試算")).to_be_visible()
    context.storage_state(path=path)
    context.close()
    return path


@pytest.fixture
def user_page(new_context, auth_state):
    """已經登入的頁面：直接載入存好的登入狀態，不用再走一次登入畫面。"""
    context = new_context(storage_state=auth_state)      # new_context 是 pytest-playwright 提供的 fixture
    return context.new_page()
