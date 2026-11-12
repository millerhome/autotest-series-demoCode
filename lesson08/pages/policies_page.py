from playwright.sync_api import Page, expect

from pages.grid import PolicyGrid
from pages.webforms import by_id_suffix


class PoliciesPage:
    """保單查詢頁（WebForms + UpdatePanel）。"""

    URL = "/webforms/Policies.aspx"

    def __init__(self, page: Page):
        self.page = page
        self.keyword = by_id_suffix(page, "txtKeyword")
        self.search_button = page.get_by_role("button", name="查詢")
        self.progress = by_id_suffix(page, "UpdateProgress1")
        self.count = by_id_suffix(page, "lblCount")
        self.grid = PolicyGrid(by_id_suffix(page, "gvPolicies"))

    def open(self):
        self.page.goto(self.URL)
        return self

    def search(self, keyword: str, expected_count: int):
        """查詢。UpdatePanel 是局部更新：要等筆數變成預期的值，才代表新的結果已經換上來。"""
        self.keyword.fill(keyword)
        self.search_button.click()
        expect(self.count).to_have_text(f"共 {expected_count} 筆")

    def go_to_page(self, number: int):
        self.page.locator(".pager").get_by_role("link", name=str(number), exact=True).click()
        expect(self.page.locator(".pager span")).to_have_text(str(number))      # 目前頁碼變成純文字

    def cancel(self, policy_no: str):
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.grid.row(policy_no).get_by_role("link", name="註銷").click()
        expect(self.grid.cell(policy_no, "狀態")).to_have_text("已註銷")
