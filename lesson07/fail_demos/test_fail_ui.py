from playwright.sync_api import Page, expect


def test_strict_mode(user_page: Page):
    user_page.goto("/policies")
    user_page.get_by_role("spinbutton").fill("30")            # 年齡與天數都是數字輸入框


def test_assert_without_waiting(user_page: Page):
    page = user_page
    page.goto("/quote")
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_role("button", name="試算").click()

    assert page.get_by_role("status").inner_text() == "保費 150 元"     # 馬上讀：結果還沒回來


def test_wrong_expectation(user_page: Page):
    page = user_page
    page.goto("/quote")
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_role("button", name="試算").click()

    expect(page.get_by_role("status")).to_have_text("保費 200 元")


def test_element_not_found(user_page: Page):
    user_page.goto("/quote")
    user_page.get_by_role("button", name="送出").click(timeout=3000)     # 畫面上沒有這個按鈕
