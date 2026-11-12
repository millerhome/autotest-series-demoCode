"""服務說成功，到資料庫確認真的寫對了。"""
from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.db


def create(api, customer, age=30, days=5):
    return api("POST", "/api/policies", json={**customer, "age": age, "days": days})


@pytest.mark.smoke
def test_create_writes_policy_row(api, db, customer_data):
    r = create(api, customer_data, age=70, days=10)
    assert r.status_code == 201, r.text
    policy_no = r.json()["policy_no"]

    row = db.execute("SELECT * FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()

    assert row is not None, f"資料庫裡找不到 {policy_no}"
    assert (row["age"], row["days"], row["status"]) == (70, 10, "active")
    assert row["premium"] == r.json()["premium"] == 450          # 回應與資料庫要一致


def test_create_writes_customer_row(api, db, customer_data):
    create(api, customer_data)

    rows = db.execute("SELECT name, phone FROM customers WHERE id_no = ?",
                      (customer_data["id_no"],)).fetchall()

    assert len(rows) == 1
    assert rows[0]["name"] == customer_data["name"]
    assert rows[0]["phone"] == customer_data["phone"]


def test_create_writes_audit(api, db, customer_data):
    policy_no = create(api, customer_data).json()["policy_no"]

    actions = [r["action"] for r in
               db.execute("SELECT action FROM policy_audit WHERE policy_no = ? ORDER BY audit_id",
                          (policy_no,))]

    assert actions == ["CREATE"]


def test_created_at_is_now(api, db, customer_data):
    policy_no = create(api, customer_data).json()["policy_no"]

    value = db.execute("SELECT created_at FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()[0]

    age = datetime.now(timezone.utc) - datetime.fromisoformat(value)
    assert timedelta(0) <= age < timedelta(seconds=10)            # 時間用「範圍」驗證


def test_same_customer_is_not_duplicated(api, db, customer_data):
    create(api, customer_data)
    create(api, customer_data, days=7)

    n_customers = db.execute("SELECT COUNT(*) FROM customers WHERE id_no = ?",
                             (customer_data["id_no"],)).fetchone()[0]
    n_policies = db.execute("SELECT COUNT(*) FROM policies p JOIN customers c"
                            " ON c.customer_id = p.customer_id WHERE c.id_no = ?",
                            (customer_data["id_no"],)).fetchone()[0]

    assert (n_customers, n_policies) == (1, 2)


def test_rejected_request_leaves_nothing(api, db, customer_data):
    r = create(api, customer_data, age=81)
    assert r.status_code == 422

    n = db.execute("SELECT COUNT(*) FROM customers WHERE id_no = ?",
                   (customer_data["id_no"],)).fetchone()[0]

    assert n == 0, "請求被拒絕了，資料庫卻留下了客戶資料"


def test_cancel_updates_status_and_audit(api, db, customer_data):
    policy_no = create(api, customer_data).json()["policy_no"]

    r = api("POST", f"/api/policies/{policy_no}/cancel")
    assert r.status_code == 200

    status = db.execute("SELECT status FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()[0]
    actions = [r["action"] for r in
               db.execute("SELECT action FROM policy_audit WHERE policy_no = ? ORDER BY audit_id",
                          (policy_no,))]
    assert status == "cancelled"
    assert actions == ["CREATE", "CANCEL"]
