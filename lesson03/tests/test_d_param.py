import pytest
from premium import calc_premium


@pytest.mark.parametrize("age, expected", [
    (17, 120),
    (18, 150),
    (64, 150),
    (65, 225),
])
def test_age_bands(age, expected):
    assert calc_premium(age, 5) == expected


@pytest.mark.parametrize("age, days", [
    pytest.param(-1, 5, id="年齡為負"),
    pytest.param(81, 5, id="超過承保上限"),
    pytest.param(30, 0, id="天數為零"),
])
def test_invalid_input(age, days):
    with pytest.raises(ValueError):
        calc_premium(age, days)


@pytest.mark.parametrize("age", [17, 30, 70])
@pytest.mark.parametrize("days", [1, 30])
def test_premium_is_positive(age, days):
    assert calc_premium(age, days) > 0
