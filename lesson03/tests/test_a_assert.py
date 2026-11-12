import pytest
from premium import calc_premium


def test_adult_five_days():
    # Arrange：準備
    age, days = 30, 5
    # Act：執行
    result = calc_premium(age, days)
    # Assert：驗證
    assert result == 150


def test_many_kinds_of_assert():
    quote = {"premium": 150, "currency": "TWD", "items": ["意外", "醫療"]}
    assert quote["premium"] > 0
    assert quote["currency"] in ("TWD", "USD")
    assert "醫療" in quote["items"]
    assert len(quote["items"]) == 2
    assert quote.get("discount") is None
    assert isinstance(quote["premium"], int)


def test_float_needs_approx():
    assert 0.1 + 0.2 != 0.3
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert 30 * 5 * 0.8 == pytest.approx(120)
