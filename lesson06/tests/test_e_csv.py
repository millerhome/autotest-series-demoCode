"""資料驅動：案例放在 CSV，不會寫程式的人也能維護。"""
import csv
from pathlib import Path

import pytest

CASES_FILE = Path(__file__).parent.parent / "data" / "quote_cases.csv"


def load_cases():
    with open(CASES_FILE, encoding="utf-8", newline="") as f:
        return [pytest.param(int(row["age"]), int(row["days"]), int(row["expected"]), id=row["案例"])
                for row in csv.DictReader(f)]


@pytest.mark.parametrize("age, days, expected", load_cases())
def test_quote_from_csv(api, age, days, expected):
    r = api("GET", "/api/quote", params={"age": age, "days": days})

    assert r.status_code == 200
    assert r.json()["premium"] == expected
