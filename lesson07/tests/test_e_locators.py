"""各種找元素的方式。"""
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def test_locator_kinds(user_page: Page):
    page = user_page
    page.goto("/policies")

    expect(page.get_by_role("heading", name="保單管理")).to_be_visible()          # 角色 + 名稱
    expect(page.get_by_label("要保人")).to_be_editable()                          # 表單欄位的標籤
    expect(page.get_by_placeholder("輸入要保人姓名")).to_be_visible()             # 提示文字
    expect(page.get_by_text("保單清單")).to_be_visible()                          # 畫面上的文字
    expect(page.get_by_test_id("policy-count")).to_contain_text("筆")             # data-testid
    expect(page.locator("table thead th")).to_have_count(7)                       # CSS：最後的手段


def test_chaining_and_filter(user_page: Page, holder):
    page = user_page
    r = page.request.post("/api/policies", data={"holder": holder, "age": 30, "days": 5})
    no = r.json()["no"]
    page.goto("/policies")

    row = page.get_by_role("row").filter(has_text=no)                   # 先找到那一列
    expect(row.get_by_role("cell").first).to_have_text(no)              # 再在列裡面找
    expect(row.get_by_role("button", name="註銷")).to_be_visible()

    same_row = page.get_by_role("row").filter(has=page.get_by_role("button", name=f"註銷 {no}"))
    expect(same_row).to_contain_text(holder)


def test_read_whole_column(user_page: Page, holder):
    page = user_page
    for suffix in ("甲", "乙", "丙"):
        page.request.post("/api/policies", data={"holder": holder + suffix, "age": 30, "days": 5})
    page.goto("/policies")
    page.get_by_label("搜尋").fill(holder)
    rows = page.locator("tbody tr")
    expect(rows).to_have_count(3)

    names = rows.locator("td:nth-child(2)").all_inner_texts()

    assert names == [holder + "甲", holder + "乙", holder + "丙"]
