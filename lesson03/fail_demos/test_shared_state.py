cart = []          # 模組層級的共用變數：所有測試共用同一個


def test_add_one():
    cart.append("旅平險")
    assert len(cart) == 1


def test_cart_starts_empty():
    assert cart == []
