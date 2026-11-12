"""有些狀態用 API 做不出來：直接在資料庫準備資料。"""
import pytest

pytestmark = pytest.mark.db


def test_read_policy_prepared_in_db(api, make_policy):
    policy_no = make_policy(age=10, days=3, premium=72)

    r = api("GET", f"/api/policies/{policy_no}")

    assert r.status_code == 200
    assert (r.json()["age"], r.json()["premium"], r.json()["status"]) == (10, 72, "active")


@pytest.mark.parametrize("status", ["expired", "cancelled"])
def test_cannot_cancel_inactive_policy(api, db, make_policy, status):
    policy_no = make_policy(status=status)

    r = api("POST", f"/api/policies/{policy_no}/cancel")

    assert r.status_code == 409
    row = db.execute("SELECT status FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()
    assert row["status"] == status                    # 資料沒有被改動
    n = db.execute("SELECT COUNT(*) FROM policy_audit WHERE policy_no = ?", (policy_no,)).fetchone()[0]
    assert n == 0                                     # 也沒有多出稽核紀錄
