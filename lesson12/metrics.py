"""從歷次執行的 JUnit XML 整理出指標。用法：python metrics.py history"""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def load(folder):
    runs = []
    for f in sorted(Path(folder).glob("*.xml")):
        cases = {}
        for c in ET.parse(f).getroot().iter("testcase"):
            failed = c.find("failure") is not None or c.find("error") is not None
            cases[f"{c.get('classname').split('.')[-1]}::{c.get('name')}"] = (failed, float(c.get("time", 0)))
        runs.append((f.stem, cases))
    return runs


def main():
    runs = load(sys.argv[1])
    print("每次執行")
    for day, cases in runs:
        failed = sum(1 for f, _ in cases.values() if f)
        total_time = sum(t for _, t in cases.values())
        print(f"  {day}　{len(cases)} 支　失敗 {failed}　通過率 {100 * (len(cases) - failed) / len(cases):5.1f}%　{total_time:4.1f} 秒")

    fails, times = defaultdict(int), defaultdict(list)
    for _, cases in runs:
        for name, (failed, t) in cases.items():
            fails[name] += failed
            times[name].append(t)
    n = len(runs)
    print(f"\n時好時壞的測試（{n} 次中有失敗、也有通過）")
    for name, k in sorted(fails.items(), key=lambda x: -x[1]):
        if 0 < k < n:
            print(f"  {name}　失敗 {k}／{n}")
    print("\n平均最慢的 3 支")
    for name, ts in sorted(times.items(), key=lambda x: -sum(x[1]) / len(x[1]))[:3]:
        print(f"  {name}　平均 {sum(ts) / len(ts):.2f} 秒")


if __name__ == "__main__":
    main()
