"""開發人員補上 label 之後（USE_LABELS=1），欄位可以改用 get_by_label。"""
from playwright.sync_api import Page, expect

from pages.quote_page import QuotePage


class QuotePageWithLabels(QuotePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.age = page.get_by_label("年齡")          # 原本：by_id_suffix(page, "txtAge")
        self.days = page.get_by_label("天數")         # 原本：by_id_suffix(page, "txtDays")


def test_quote_with_labels(page: Page):
    q = QuotePageWithLabels(page).open()
    q.calculate(age=30, days=5)

    expect(q.result).to_have_text("保費 150 元")
