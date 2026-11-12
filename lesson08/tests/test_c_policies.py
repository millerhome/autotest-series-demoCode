import pytest
from playwright.sync_api import expect

from pages.policies_page import PoliciesPage

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_first_page(policies_page: PoliciesPage):
    expect(policies_page.count).to_have_text("共 7 筆")
    expect(policies_page.grid.rows).to_have_count(5)             # 每頁五筆
    assert policies_page.grid.column_texts("要保人") == ["王小明", "林小美", "陳小華", "張大同", "李美玲"]


def test_search(policies_page: PoliciesPage):
    policies_page.search("小", expected_count=3)

    expect(policies_page.grid.rows).to_have_count(3)
    assert policies_page.grid.column_texts("要保人") == ["王小明", "林小美", "陳小華"]


def test_search_no_result(policies_page: PoliciesPage):
    policies_page.search("查無此人", expected_count=0)

    expect(policies_page.grid.root).to_contain_text("查無資料")


def test_paging(policies_page: PoliciesPage):
    policies_page.go_to_page(2)

    expect(policies_page.grid.rows).to_have_count(2)
    assert policies_page.grid.column_texts("保單號碼") == ["TP000006", "TP000007"]


def test_cancel(policies_page: PoliciesPage):
    policies_page.cancel("TP000002")

    expect(policies_page.grid.cell("TP000002", "狀態")).to_have_text("已註銷")
    expect(policies_page.grid.row("TP000002").get_by_role("link")).to_have_count(0)
    expect(policies_page.grid.cell("TP000001", "狀態")).to_have_text("有效")         # 其他列不受影響


def test_progress_is_hidden_when_done(policies_page: PoliciesPage):
    policies_page.search("王", expected_count=1)

    expect(policies_page.progress).to_be_hidden()
