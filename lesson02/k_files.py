import csv
import json
from pathlib import Path

here = Path(__file__).parent

with open(here / "rates.json", encoding="utf-8") as f:   # with ≈ C# 的 using
    rates = json.load(f)                                  # JSON → dict
print(rates["base_per_day"], len(rates["age_bands"]))

with open(here / "tests" / "cases.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))                        # 每列是一個 dict
print(rows[0])
