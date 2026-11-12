import pytest
from premium import calc_premium


def test_adult_five_days():
    assert calc_premium(age=30, days=5) == 150


@pytest.mark.parametrize(
    "age, days, expected",
    [
        (17, 5, 120),   # 未成年 0.8
        (18, 5, 150),   # 邊界：剛滿 18
        (64, 5, 150),   # 邊界：65 的前一歲
        (65, 5, 225),   # 邊界：剛滿 65，係數 1.5
        (80, 1, 45),    # 承保上限
    ],
)
def test_premium_by_age(age, days, expected):
    assert calc_premium(age, days) == expected


@pytest.mark.parametrize("age, days", [(-1, 5), (81, 5), (30, 0)])
def test_invalid_input_is_rejected(age, days):
    with pytest.raises(ValueError):
        calc_premium(age, days)
