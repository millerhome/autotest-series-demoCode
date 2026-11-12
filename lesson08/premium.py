"""旅平險保費試算：規則放在 rates.json，程式只負責計算。"""
import json
from pathlib import Path

RATES_FILE = Path(__file__).parent / "rates.json"


def load_rates(path=RATES_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def age_factor(age, rates):
    if age < rates["min_age"] or age > rates["max_age"]:
        raise ValueError("年齡不在承保範圍")
    for band in rates["age_bands"]:
        if age < band["below"]:
            return band["factor"]


def calc_premium(age, days, rates=None):
    if rates is None:
        rates = load_rates()
    if days < 1:
        raise ValueError("天數至少 1 天")
    return round(rates["base_per_day"] * days * age_factor(age, rates))
