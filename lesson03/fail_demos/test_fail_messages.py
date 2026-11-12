from premium import calc_premium


def test_number():
    assert calc_premium(65, 5) == 150


def test_dict():
    actual = {"no": "TP001", "holder": "王小明", "premium": 150, "days": 5}
    expected = {"no": "TP001", "holder": "王小明", "premium": 120, "days": 5}
    assert actual == expected


def test_list():
    assert ["意外", "醫療", "不便"] == ["意外", "醫療"]


def test_text():
    message = "保單 TP001 已成立，保費 150 元"
    assert "保費 120 元" in message


def test_custom_message():
    premium = calc_premium(70, 5)
    assert premium <= 200, f"70 歲 5 天的保費 {premium} 超過上限 200"
