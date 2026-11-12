import sys
import time

import pytest
from premium import calc_premium


@pytest.mark.smoke
def test_basic_quote():
    assert calc_premium(30, 1) == 30


@pytest.mark.regression
def test_senior_long_trip():
    assert calc_premium(70, 30) == 1350


@pytest.mark.skip(reason="團體險規則尚未定案")
def test_group_policy():
    ...


@pytest.mark.skipif(sys.platform != "win32", reason="只在 Windows 執行")
def test_windows_only():
    ...


@pytest.mark.xfail(reason="已知問題：0 天應改為回傳 0，待修正")
def test_zero_days_returns_zero():
    assert calc_premium(30, 0) == 0


@pytest.mark.slow
@pytest.mark.regression
def test_batch_quotes():
    time.sleep(0.3)                      # 模擬一支比較慢的測試
    assert all(calc_premium(a, 5) > 0 for a in range(0, 81))
