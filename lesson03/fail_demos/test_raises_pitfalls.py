import pytest
from premium import calc_premium


def test_assert_inside_with_never_runs():
    with pytest.raises(ValueError):
        calc_premium(81, 5)
        assert 1 == 2          # 上一行已經丟出例外，這一行永遠不會執行


def test_no_exception_raised():
    with pytest.raises(ValueError):
        calc_premium(80, 5)    # 80 歲在承保範圍內，不會丟例外
