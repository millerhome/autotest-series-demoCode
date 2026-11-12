import pytest
from playwright.sync_api import expect

from pages.quote_page import QuotePage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_quote_asia_basic(quote_page: QuotePage):
    quote_page.calculate(age=30, days=5)

    expect(quote_page.result).to_have_text("保費 150 元")


def test_values_survive_postback(quote_page: QuotePage):
    quote_page.calculate(age=30, days=5)

    expect(quote_page.result).to_have_text("保費 150 元")
    expect(quote_page.age).to_have_value("30")              # postback 之後，輸入的值還在
    expect(quote_page.days).to_have_value("5")


def test_region_changes_plans(quote_page: QuotePage):
    quote_page.select_region("歐洲", first_plan="申根基本型")

    expect(quote_page.plan.locator("option")).to_have_text(["申根基本型", "申根豪華型"])


def test_quote_europe_plus(quote_page: QuotePage):
    quote_page.select_region("歐洲", first_plan="申根基本型")
    quote_page.calculate(age=30, days=5, plan="申根豪華型")

    expect(quote_page.result).to_have_text("保費 270 元")


@pytest.mark.parametrize("age, days, messages", [
    pytest.param("", "5", ["請輸入年齡"], id="年齡沒填"),
    pytest.param("", "", ["請輸入年齡", "請輸入天數"], id="都沒填"),
    pytest.param("81", "5", ["年齡不在承保範圍"], id="超過承保上限"),
])
def test_quote_validation(quote_page: QuotePage, age, days, messages):
    quote_page.calculate(age=age, days=days)

    expect(quote_page.errors).to_have_text(messages)
    expect(quote_page.result).to_be_empty()
