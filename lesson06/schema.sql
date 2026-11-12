CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    id_no       TEXT NOT NULL UNIQUE,
    phone       TEXT
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_no   TEXT UNIQUE,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    age         INTEGER NOT NULL,
    days        INTEGER NOT NULL,
    premium     INTEGER NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'expired')),
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policy_audit (
    audit_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_no   TEXT NOT NULL,
    action      TEXT NOT NULL,
    logged_at   TEXT NOT NULL
);
