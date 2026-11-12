"""審查前的自動檢查：找出測試檔裡常見的問題。只能抓「看得出來的」，不能取代人工審查。"""
import re
import sys
from pathlib import Path

RULES = [
    (r"time\.sleep\(", "使用了固定等待 time.sleep"),
    (r"https?://", "程式裡寫死了網址"),
    (r"from premium import|calc_premium\(", "用產品程式計算預期值"),
    (r"password\s*=\s*[\"'][^\"']+[\"']", "程式裡寫死了密碼"),
    (r"^\s*for .+ in .+:\s*$", "測試裡用迴圈，考慮改用 parametrize"),
]
REQUEST = re.compile(r"\.(get|post|put|delete|request)\(")


def check(path: Path):
    problems = []
    for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = line.split("#", 1)[0]
        for pattern, message in RULES:
            if re.search(pattern, code):
                problems.append((no, message))
        if REQUEST.search(code) and "timeout" not in code:
            problems.append((no, "HTTP 請求沒有 timeout"))
    return problems


if __name__ == "__main__":
    total = 0
    for name in sys.argv[1:]:
        for path in sorted(Path(name).rglob("test_*.py")):
            for no, message in check(path):
                print(f"{path}:{no}: {message}")
                total += 1
    print(f"共 {total} 個可能的問題")
    sys.exit(1 if total else 0)
