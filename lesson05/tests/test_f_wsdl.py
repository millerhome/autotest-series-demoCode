import difflib
import os
from pathlib import Path

import pytest

from wsdl_summary import summarize

SNAPSHOT = Path(__file__).parent / "snapshots" / "PolicyService.txt"


@pytest.mark.contract
def test_wsdl_matches_snapshot(ws_url):
    current = summarize(ws_url + "?WSDL")

    if os.environ.get("UPDATE_SNAPSHOT") == "1":        # 確認是約定好的變更後，才更新快照
        SNAPSHOT.write_text(current, encoding="utf-8")

    expected = SNAPSHOT.read_text(encoding="utf-8")
    diff = "\n".join(difflib.unified_diff(expected.splitlines(), current.splitlines(),
                                          "快照（約定的介面）", "目前的 WSDL", lineterm=""))
    assert current == expected, "WSDL 介面與快照不同：\n" + diff
