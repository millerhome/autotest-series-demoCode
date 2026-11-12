import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.ui


def row_of(page: Page, text):
    """找出保單清單裡，包含指定文字的那一列。"""
    return page.get_by_role("row").filter(has_text=text)


@pytest.mark.smoke
def test_add_policy(login: Page, holder):
    page = login
    page.get_by_role("link", name="保單管理").click()

    page.get_by_label("要保人").fill(holder)
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_role("button", name="新增保單").click()

    row = row_of(page, holder)
    expect(row).to_be_visible()
    expect(row.get_by_role("cell").nth(4)).to_have_text("150")
    expect(row.get_by_role("cell").nth(5)).to_have_text("有效")
    expect(page.get_by_label("要保人")).to_be_empty()          # 新增成功後表單會清空


def test_policy_created_by_api_is_listed(login: Page, make_policy, holder):
    policy = make_policy(holder, age=70, days=10)

    login.goto("/policies")

    row = row_of(login, policy["no"])
    expect(row).to_contain_text(holder)
    expect(row).to_contain_text("450")


def test_cancel_policy(login: Page, make_policy, holder):
    page = login
    policy = make_policy(holder)
    page.goto("/policies")

    page.once("dialog", lambda dialog: dialog.accept())          # 先講好：出現確認視窗就按「確定」
    page.get_by_role("button", name=f"註銷 {policy['no']}").click()

    row = row_of(page, policy["no"])
    expect(row).to_contain_text("已註銷")
    expect(row.get_by_role("button")).to_have_count(0)           # 註銷之後，按鈕不見了


def test_dismiss_cancel_dialog(login: Page, make_policy, holder):
    page = login
    policy = make_policy(holder)
    page.goto("/policies")
    messages = []

    def on_dialog(dialog):
        messages.append(dialog.message)
        dialog.dismiss()                                         # 按「取消」
    page.once("dialog", on_dialog)
    page.get_by_role("button", name=f"註銷 {policy['no']}").click()

    assert messages == [f"確定要註銷保單 {policy['no']} 嗎？"]
    expect(row_of(page, policy["no"])).to_contain_text("有效")


def test_search(login: Page, make_policy, holder):
    page = login
    make_policy(holder + "甲")
    make_policy(holder + "乙")
    page.goto("/policies")

    page.get_by_label("搜尋").fill(holder)
    expect(page.get_by_role("row").filter(has_text=holder)).to_have_count(2)
    expect(page.get_by_test_id("policy-count")).to_have_text("共 2 筆")

    page.get_by_label("搜尋").fill(holder + "乙")
    expect(page.get_by_test_id("policy-count")).to_have_text("共 1 筆")

    page.get_by_label("搜尋").fill("查無此人")
    expect(page.get_by_text("目前沒有符合的保單")).to_be_visible()


def test_add_policy_validation(login: Page):
    page = login
    page.goto("/policies")

    page.get_by_role("button", name="新增保單").click()

    expect(page.get_by_role("alert")).to_have_text("要保人姓名不可空白")
