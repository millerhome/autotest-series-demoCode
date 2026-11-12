import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_login_page(page: Page):
    page.goto("/login")

    expect(page).to_have_title(re.compile("登入"))
    expect(page.get_by_role("heading", name="登入")).to_be_visible()


@pytest.mark.smoke
def test_user_can_login(page: Page):
    page.goto("/login")

    page.get_by_label("帳號").fill("tester")
    page.get_by_label("密碼").fill("test-pass-123")
    page.get_by_role("button", name="登入").click()

    expect(page).to_have_url(re.compile("/quote$"))
    expect(page.get_by_text("歡迎，tester")).to_be_visible()


def test_wrong_password(page: Page):
    page.goto("/login")

    page.get_by_label("帳號").fill("tester")
    page.get_by_label("密碼").fill("wrong")
    page.get_by_role("button", name="登入").click()

    expect(page.get_by_role("alert")).to_have_text("帳號或密碼錯誤")
    expect(page).to_have_url(re.compile("/login$"))


def test_must_login_first(page: Page):
    page.goto("/policies")

    expect(page).to_have_url(re.compile("/login$"))
