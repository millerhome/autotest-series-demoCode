"""擷取練習網站的畫面，給教材使用。"""
import threading
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import policy_web

OUT = Path(__file__).parent.parent.parent / "public" / "img" / "l07"
server = policy_web.make_server()
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(base_url=base, viewport={"width": 1180, "height": 440}, device_scale_factor=2, locale="zh-TW")
    page = ctx.new_page()
    page.goto("/login")
    page.get_by_label("帳號").fill("tester")
    page.screenshot(path=OUT / "login.png")
    page.get_by_label("密碼").fill("test-pass-123")
    page.get_by_role("button", name="登入").click()
    page.get_by_label("年齡").fill("30")
    page.get_by_label("天數").fill("5")
    page.get_by_role("button", name="試算").click()
    expect(page.get_by_role("status")).to_have_text("計算中…")
    page.screenshot(path=OUT / "quote-loading.png")
    expect(page.get_by_role("status")).to_have_text("保費 150 元")
    page.screenshot(path=OUT / "quote.png")
    for holder, age, days in [("測試_王小明", 30, 5), ("測試_林小美", 70, 10), ("測試_陳小華", 10, 3)]:
        page.request.post("/api/policies", data={"holder": holder, "age": age, "days": days})
    page.request.post("/api/policies/TP000002/cancel")
    page.goto("/policies")
    expect(page.get_by_role("row")).to_have_count(4)
    page.screenshot(path=OUT / "policies.png")
    print(page.get_by_role("main").aria_snapshot())
    browser.close()
