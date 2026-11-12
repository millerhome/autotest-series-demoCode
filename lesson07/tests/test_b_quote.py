import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_quote_adult(login: Page):
    page = login
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_role("button", name="試算").click()

    expect(page.get_by_role("status")).to_have_text("保費 150 元")


def test_quote_with_plan_and_addon(login: Page):
    page = login
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_label("方案").select_option("豪華型")
    page.get_by_label("加購不便險").check()
    page.get_by_role("button", name="試算").click()

    expect(page.get_by_label("加購不便險")).to_be_checked()
    expect(page.get_by_label("方案")).to_have_value("plus")
    expect(page.get_by_role("status")).to_have_text("保費 275 元")


def test_press_enter_to_quote(login: Page):
    page = login
    page.get_by_label("年齡").fill("70")
    page.get_by_label("天數").fill("10")
    page.get_by_label("天數").press("Enter")

    expect(page.get_by_role("status")).to_have_text("保費 450 元")


@pytest.mark.parametrize("age, days, message", [
    pytest.param("81", "5", "年齡不在承保範圍", id="超過承保上限"),
    pytest.param("30", "0", "天數至少 1 天", id="天數為零"),
    pytest.param("", "5", "年齡與天數必須是整數", id="年齡沒填"),
])
def test_quote_errors(login: Page, age, days, message):
    page = login
    page.get_by_label("年齡").fill(age)
    page.get_by_label("天數").fill(days)
    page.get_by_role("button", name="試算").click()

    expect(page.get_by_role("alert")).to_have_text(message)
    expect(page.get_by_role("status")).to_be_empty()


def test_button_disabled_while_loading(login: Page):
    page = login
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    button = page.get_by_role("button", name="試算")
    button.click()

    expect(button).to_be_disabled()
    expect(page.get_by_role("status")).to_have_text("計算中…")
    expect(page.get_by_role("status")).to_have_text("保費 150 元")
    expect(button).to_be_enabled()
