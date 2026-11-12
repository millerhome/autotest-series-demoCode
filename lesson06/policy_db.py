"""資料庫的連線與初始化。練習用 SQLite；公司環境換成 Oracle 或 SQL Server 的連線即可。"""
import sqlite3
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


def connect(db_path):
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row            # 查詢結果可以用欄位名稱取值
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite 預設不檢查外來鍵，要自己打開
    return conn


def init_db(db_path):
    conn = connect(db_path)
    conn.executescript(SCHEMA)
    conn.close()
