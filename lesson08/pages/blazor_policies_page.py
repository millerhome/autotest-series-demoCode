from playwright.sync_api import Page, expect

from pages.grid import PolicyGrid


class BlazorPoliciesPage:
    """新版保單管理頁（Blazor）。"""

    URL = "/blazor/policies"

    def __init__(self, page: Page):
        self.page = page
        self.app = page.locator("#app")
        self.holder = page.get_by_label("要保人")
        self.age = page.get_by_label("年齡")
        self.days = page.get_by_label("天數")
        self.add_button = page.get_by_role("button", name="新增保單")
        self.error = page.get_by_role("alert")
        self.keyword = page.get_by_label("搜尋")
        self.count = page.get_by_test_id("count")
        self.grid = PolicyGrid(page.locator("#list"))

    def open(self):
        """開啟頁面，並等到「可以互動」而且資料載入完成。"""
        self.page.goto(self.URL)
        expect(self.app).to_have_attribute("data-interactive", "true")     # 事件已經接上
        expect(self.count).to_be_visible()                                  # 清單已經載入
        return self

    def add(self, holder: str, age, days):
        self.holder.fill(holder)
        self.age.fill(str(age))
        self.days.fill(str(days))
        self.add_button.click()

    def filter(self, keyword: str, expected_count: int):
        self.keyword.fill(keyword)
        expect(self.count).to_have_text(f"共 {expected_count} 筆")
