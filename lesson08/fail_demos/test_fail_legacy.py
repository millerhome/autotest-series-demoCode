from playwright.sync_api import Page, expect

from pages.blazor_policies_page import BlazorPoliciesPage
from pages.policies_page import PoliciesPage
from pages.quote_page import QuotePage


def test_label_does_not_work(page: Page):
    page.goto("/webforms/Quote.aspx")
    page.get_by_label("年齡").fill("30", timeout=3000)             # 「年齡」只是 span，不是 label


def test_read_options_during_autopostback(page: Page):
    q = QuotePage(page).open()
    q.region.select_option("歐洲")                                  # 觸發 AutoPostBack，但是沒有等它完成

    assert q.plan.locator("option").all_inner_texts() == ["申根基本型", "申根豪華型"]


def test_actions_during_autopostback_still_work(page: Page):
    q = QuotePage(page).open()
    q.region.select_option("歐洲")                                  # 沒有等 postback 完成就繼續操作
    q.calculate(age=30, days=5, plan="申根豪華型")

    expect(q.result).to_have_text("保費 270 元")


def test_read_grid_too_early(page: Page):
    p = PoliciesPage(page).open()
    p.keyword.fill("小")
    p.search_button.click()

    assert p.grid.column_texts("要保人") == ["王小明", "林小美", "陳小華"]     # 局部更新還沒回來就讀


def test_click_before_interactive(page: Page):
    b = BlazorPoliciesPage(page)
    page.goto(b.URL)                                                # 沒有等「可以互動」
    b.add("趙小蘭", age=30, days=5)

    expect(b.grid.row("趙小蘭")).to_be_visible(timeout=3000)
