import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.ui
def test_user_can_get_a_quote(page: Page, base_url):
    page.goto(base_url)

    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_role("button", name="試算").click()

    expect(page.get_by_role("status")).to_have_text("保費 150 元")
