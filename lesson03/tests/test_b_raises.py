import pytest
from premium import calc_premium


def test_age_over_limit():
    with pytest.raises(ValueError):
        calc_premium(81, 5)


def test_error_message():
    with pytest.raises(ValueError, match="天數至少 1 天"):
        calc_premium(30, 0)


def test_inspect_exception():
    with pytest.raises(ValueError) as excinfo:
        calc_premium(-1, 5)
    assert "承保範圍" in str(excinfo.value)
