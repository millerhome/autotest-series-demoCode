from playwright.sync_api import Page, expect

from pages.webforms import by_id_suffix


class QuotePage:
    """保費試算頁（WebForms）。測試只跟這個類別打交道，不直接碰 locator。"""

    URL = "/webforms/Quote.aspx"

    def __init__(self, page: Page):
        self.page = page
        self.region = by_id_suffix(page, "ddlRegion")
        self.plan = by_id_suffix(page, "ddlPlan")
        self.age = by_id_suffix(page, "txtAge")
        self.days = by_id_suffix(page, "txtDays")
        self.calc_button = page.get_by_role("button", name="試算")
        self.result = by_id_suffix(page, "lblResult")
        self.errors = page.locator(".err")

    def open(self):
        self.page.goto(self.URL)
        return self

    def select_region(self, name: str, first_plan: str):
        """選擇地區。地區是 AutoPostBack：選了之後整頁會重新載入，要等方案清單換好才算完成。"""
        self.region.select_option(name)
        expect(self.plan.locator("option").first).to_have_text(first_plan)

    def calculate(self, age, days, plan: str | None = None):
        if plan:
            self.plan.select_option(plan)
        self.age.fill(str(age))
        self.days.fill(str(days))
        self.calc_button.click()
