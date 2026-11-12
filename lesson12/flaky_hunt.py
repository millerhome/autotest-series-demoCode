"""把同一套測試重複執行 N 次，找出「有時過、有時不過」的測試。

用法：python flaky_hunt.py 20 [pytest 的其他參數]
      python flaky_hunt.py each        每支測試單獨執行一次，找出依賴其他測試的
"""
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def run_once(extra, junit):
    subprocess.run([sys.executable, "-m", "pytest", "-q", f"--junitxml={junit}", *extra],
                   capture_output=True, text=True)
    results = {}
    for case in ET.parse(junit).getroot().iter("testcase"):
        name = f"{case.get('classname')}::{case.get('name')}"
        failed = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None
        results[name] = "skip" if skipped else ("fail" if failed else "pass")
    return results


def run_each():
    ids = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "--run-quarantine"],
                         capture_output=True, text=True).stdout.splitlines()
    ids = [i for i in ids if i.startswith("tests/") and "::" in i]
    bad = 0
    for test_id in ids:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--run-quarantine", test_id],
                           capture_output=True, text=True)
        if r.returncode != 0:
            bad += 1
            print(f"  單獨執行會失敗：{test_id}")
    print(f"共 {len(ids)} 支，單獨執行會失敗的 {bad} 支")


def main():
    if sys.argv[1] == "each":
        return run_each()
    times = int(sys.argv[1])
    extra = sys.argv[2:]
    tally = defaultdict(lambda: {"pass": 0, "fail": 0, "skip": 0})
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(times):
            for name, outcome in run_once(extra, Path(tmp) / f"r{i}.xml").items():
                tally[name][outcome] += 1
    print(f"執行 {times} 次的結果")
    flaky = 0
    for name, c in sorted(tally.items()):
        runs = c["pass"] + c["fail"]
        label = "不穩定" if c["pass"] and c["fail"] else ("一直失敗" if c["fail"] else "穩定")
        flaky += label == "不穩定"
        if label != "穩定":
            print(f"  {label}　{name.split('.')[-1]}　通過 {c['pass']}／{runs}")
    print(f"共 {len(tally)} 支，穩定 {sum(1 for c in tally.values() if not c['fail'])}，不穩定 {flaky}")


if __name__ == "__main__":
    main()
