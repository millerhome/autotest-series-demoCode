"""補充：commit 的可見性、等待非同步寫入、用基準資料庫還原。"""
import shutil
import threading
import time

import pytest

from policy_db import connect, init_db
from testdata import wait_until

pytestmark = pytest.mark.db


def test_uncommitted_data_is_invisible(db_path, base_url):
    writer, reader = connect(db_path), connect(db_path)
    count = "SELECT COUNT(*) FROM customers WHERE id_no = 'Z166666666'"

    writer.execute("INSERT INTO customers (name, id_no) VALUES ('測試_可見性', 'Z166666666')")
    assert reader.execute(count).fetchone()[0] == 0        # 還沒 commit：另一條連線看不到

    writer.commit()
    assert reader.execute(count).fetchone()[0] == 1        # commit 之後才看得到

    writer.execute("DELETE FROM customers WHERE id_no = 'Z166666666'")
    writer.commit()
    writer.close(), reader.close()


def test_wait_for_async_write(db, db_path):
    def late_writer():                                     # 模擬：服務在背景晚 0.5 秒才寫入
        time.sleep(0.5)
        conn = connect(db_path)
        conn.execute("INSERT INTO policy_audit (policy_no, action, logged_at)"
                     " VALUES ('TP-ASYNC', 'NOTIFY', '2026-01-01')")
        conn.commit()
        conn.close()
    threading.Thread(target=late_writer).start()

    row = wait_until(lambda: db.execute(
        "SELECT action FROM policy_audit WHERE policy_no = 'TP-ASYNC'").fetchone())

    assert row["action"] == "NOTIFY"
    db.execute("DELETE FROM policy_audit WHERE policy_no = 'TP-ASYNC'")
    db.commit()


def test_wait_until_gives_up():
    with pytest.raises(AssertionError, match="等了 0.3 秒"):
        wait_until(lambda: None, timeout=0.3, interval=0.1)


@pytest.fixture(scope="module")
def baseline(tmp_path_factory):
    """基準資料庫：只建立一次，裡面放好共用的基礎資料。"""
    path = tmp_path_factory.mktemp("baseline") / "baseline.db"
    init_db(path)
    conn = connect(path)
    conn.execute("INSERT INTO customers (name, id_no) VALUES ('基準客戶', 'F100000001')")
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def fresh_db(baseline, tmp_path):
    """每支測試拿到一份基準資料庫的複本，怎麼改都不會影響別人。"""
    path = tmp_path / "copy.db"
    shutil.copy(baseline, path)
    conn = connect(path)
    yield conn
    conn.close()


def test_delete_everything(fresh_db):
    fresh_db.execute("DELETE FROM customers")
    fresh_db.commit()
    assert fresh_db.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0


def test_baseline_is_untouched(fresh_db):
    names = [r["name"] for r in fresh_db.execute("SELECT name FROM customers")]
    assert names == ["基準客戶"]             # 上一支測試刪光了它自己的複本，這裡不受影響
