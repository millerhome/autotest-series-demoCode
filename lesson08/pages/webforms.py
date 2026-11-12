"""WebForms 頁面共用的小工具。"""
from playwright.sync_api import Locator, Page


def by_id_suffix(page: Page, name: str) -> Locator:
    """用 id 的「結尾」找控制項：ctl00_MainContent_txtAge → 只要結尾是 _txtAge 就符合。

    前面的 ctl00_MainContent_ 會隨著主版頁面與容器改變，結尾的控制項名稱比較穩定。
    """
    return page.locator(f"[id$='_{name}']")
