import csv
from pathlib import Path

import pytest
from premium import calc_premium

CASES_FILE = Path(__file__).parent / "cases.csv"


def load_cases():
    with open(CASES_FILE, encoding="utf-8", newline="") as f:
        return [
            pytest.param(int(r["age"]), int(r["days"]), int(r["expected"]),
                         id=r["note"])
            for r in csv.DictReader(f)
        ]


@pytest.mark.parametrize("age, days, expected", load_cases())
def test_premium_from_csv(age, days, expected):
    assert calc_premium(age, days) == expected


def test_custom_rates():
    rates = {"base_per_day": 100, "min_age": 0, "max_age": 80,
             "age_bands": [{"below": 81, "factor": 1.0}]}
    assert calc_premium(30, 2, rates) == 200
