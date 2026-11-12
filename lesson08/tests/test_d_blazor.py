import pytest
from playwright.sync_api import expect

from pages.blazor_policies_page import BlazorPoliciesPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_list_is_loaded(blazor_page: BlazorPoliciesPage):
    expect(blazor_page.count).to_have_text("共 7 筆")
    expect(blazor_page.grid.rows).to_have_count(7)


def test_add_policy(blazor_page: BlazorPoliciesPage):
    blazor_page.add("趙小蘭", age=30, days=5)

    expect(blazor_page.count).to_have_text("共 8 筆")
    expect(blazor_page.grid.cell("趙小蘭", "保費")).to_have_text("150")
    expect(blazor_page.holder).to_be_empty()


def test_filter_as_you_type(blazor_page: BlazorPoliciesPage):
    blazor_page.filter("小", expected_count=3)

    assert blazor_page.grid.column_texts("要保人") == ["王小明", "林小美", "陳小華"]


def test_filter_no_result(blazor_page: BlazorPoliciesPage):
    blazor_page.keyword.fill("查無此人")

    expect(blazor_page.page.get_by_text("沒有符合的保單")).to_be_visible()


@pytest.mark.parametrize("holder, age, days, message", [
    pytest.param("", "30", "5", "請輸入要保人", id="要保人沒填"),
    pytest.param("趙小蘭", "81", "5", "年齡不在承保範圍", id="超過承保上限"),
    pytest.param("趙小蘭", "abc", "5", "年齡與天數必須是數字", id="年齡不是數字"),
])
def test_add_validation(blazor_page: BlazorPoliciesPage, holder, age, days, message):
    blazor_page.add(holder, age, days)

    expect(blazor_page.error).to_have_text(message)
    expect(blazor_page.count).to_have_text("共 7 筆")
