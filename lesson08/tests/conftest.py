import threading

import pytest
from playwright.sync_api import Page

from legacy_web import make_server
from pages.blazor_policies_page import BlazorPoliciesPage
from pages.policies_page import PoliciesPage
from pages.quote_page import QuotePage


@pytest.fixture(scope="session")
def base_url():
    server = make_server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}, "locale": "zh-TW"}


@pytest.fixture(autouse=True)
def reset_data(page: Page):
    """每支測試開始前，把練習網站的資料還原成七張保單（只有練習網站才有這個功能）。"""
    page.request.post("/test/reset")


@pytest.fixture
def quote_page(page: Page) -> QuotePage:
    return QuotePage(page).open()


@pytest.fixture
def policies_page(page: Page) -> PoliciesPage:
    return PoliciesPage(page).open()


@pytest.fixture
def blazor_page(page: Page) -> BlazorPoliciesPage:
    return BlazorPoliciesPage(page).open()
