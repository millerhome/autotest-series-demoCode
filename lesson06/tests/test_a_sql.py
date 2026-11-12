"""直接用 SQL 查詢資料庫：連線、查詢、參數。"""
import pytest

pytestmark = pytest.mark.db


def test_tables_exist(db):
    rows = db.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall()

    names = [r["name"] for r in rows]
    assert {"customers", "policies", "policy_audit"} <= set(names)


def test_query_with_parameters(db, make_policy):
    policy_no = make_policy(age=70, days=10, premium=450)

    row = db.execute("SELECT age, days, premium, status FROM policies WHERE policy_no = ?",
                     (policy_no,)).fetchone()

    assert dict(row) == {"age": 70, "days": 10, "premium": 450, "status": "active"}


def test_parameters_are_not_sql(db, make_policy):
    make_policy()
    evil = "x' OR '1'='1"

    rows = db.execute("SELECT * FROM customers WHERE name = ?", (evil,)).fetchall()

    assert rows == []          # 參數只會被當成資料，不會變成 SQL 的一部分
