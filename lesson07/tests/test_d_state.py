"""重複使用登入狀態：不必每支測試都從登入畫面開始。"""
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def test_open_quote_directly(user_page: Page):
    user_page.goto("/quote")

    expect(user_page.get_by_text("歡迎，tester")).to_be_visible()


def test_open_policies_directly(user_page: Page):
    user_page.goto("/policies")

    expect(user_page.get_by_role("table", name="保單清單")).to_be_visible()


def test_navigation_marks_current_page(user_page: Page):
    user_page.goto("/quote")
    nav = user_page.get_by_role("navigation", name="主選單")

    expect(nav.get_by_role("link", name="保費試算")).to_have_attribute("aria-current", "page")
    nav.get_by_role("link", name="保單管理").click()
    expect(nav.get_by_role("link", name="保單管理")).to_have_attribute("aria-current", "page")


def test_logout(user_page: Page):
    user_page.goto("/quote")

    user_page.get_by_role("link", name="登出").click()

    expect(user_page.get_by_role("heading", name="登入")).to_be_visible()
    user_page.goto("/quote")
    expect(user_page.get_by_role("heading", name="登入")).to_be_visible()      # 登出後進不去了


def test_contexts_are_isolated(user_page: Page, new_context):
    guest = new_context().new_page()              # 另一個全新的瀏覽器環境：沒有登入狀態

    user_page.goto("/policies")
    guest.goto("/policies")

    expect(user_page.get_by_role("table", name="保單清單")).to_be_visible()
    expect(guest.get_by_role("heading", name="登入")).to_be_visible()      # 被導回登入頁
