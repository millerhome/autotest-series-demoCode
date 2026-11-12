from playwright.sync_api import Locator


class PolicyGrid:
    """保單清單（表格）。WebForms 與 Blazor 兩個頁面的表格都可以用它。"""

    COLUMNS = {"保單號碼": 0, "要保人": 1, "年齡": 2, "天數": 3, "保費": 4, "狀態": 5}

    def __init__(self, root: Locator):
        self.root = root
        self.rows = root.get_by_role("row").filter(has=root.page.get_by_role("cell"))   # 不含標題列

    def row(self, text: str) -> Locator:
        return self.rows.filter(has_text=text)

    def cell(self, row_text: str, column: str) -> Locator:
        return self.row(row_text).get_by_role("cell").nth(self.COLUMNS[column])

    def column_texts(self, column: str) -> list[str]:
        return [row.get_by_role("cell").nth(self.COLUMNS[column]).inner_text() for row in self.rows.all()]
