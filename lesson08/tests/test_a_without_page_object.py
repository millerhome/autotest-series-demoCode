"""先看「沒有 Page Object」的寫法：能動，但是 locator 散落在測試裡。"""
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def test_quote_raw(page: Page):
    page.goto("/webforms/Quote.aspx")

    page.locator("#ctl00_MainContent_txtAge").fill("30")
    page.locator("#ctl00_MainContent_txtDays").fill("5")
    page.locator("#ctl00_MainContent_btnCalc").click()

    expect(page.locator("#ctl00_MainContent_lblResult")).to_have_text("保費 150 元")


def test_quote_required_raw(page: Page):
    page.goto("/webforms/Quote.aspx")

    page.locator("#ctl00_MainContent_txtDays").fill("5")
    page.locator("#ctl00_MainContent_btnCalc").click()

    expect(page.locator("#ctl00_MainContent_rfvAge")).to_have_text("請輸入年齡")
