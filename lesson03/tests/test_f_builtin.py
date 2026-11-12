import json
import os

from premium import calc_premium, load_rates


def test_tmp_path(tmp_path):
    f = tmp_path / "rates.json"
    f.write_text(json.dumps({"base_per_day": 50, "min_age": 0, "max_age": 80,
                             "age_bands": [{"below": 81, "factor": 1.0}]}),
                 encoding="utf-8")
    rates = load_rates(f)
    assert calc_premium(30, 2, rates) == 100


def test_monkeypatch_env(monkeypatch):
    monkeypatch.setenv("TEST_ENV", "sit")
    assert os.environ["TEST_ENV"] == "sit"


def test_capsys(capsys):
    print("保費 150 元")
    out = capsys.readouterr().out
    assert "150" in out
