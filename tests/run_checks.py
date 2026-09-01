#!/usr/bin/env python3
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "sample" / "sample_ap_export.csv"
SQL = ROOT / "sql" / "ap_duplicate_payment_checks.sql"
COLUMNS = ["vendor_id", "vendor_name", "invoice_number", "invoice_date", "due_date", "payment_date", "amount", "currency", "payment_reference", "status"]


def load_sample(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS ap_export")
    conn.execute("""
        CREATE TABLE ap_export (
            vendor_id TEXT, vendor_name TEXT, invoice_number TEXT, invoice_date TEXT,
            due_date TEXT, payment_date TEXT, amount REAL, currency TEXT,
            payment_reference TEXT, status TEXT
        )
    """)
    with SAMPLE.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == COLUMNS, reader.fieldnames
        rows = [[row[col] for col in COLUMNS] for row in reader]
    conn.executemany("INSERT INTO ap_export VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def run_sql(conn: sqlite3.Connection):
    statements = [s.strip() for s in SQL.read_text(encoding="utf-8").split(";") if s.strip()]
    result_sets = []
    for statement in statements:
        cur = conn.execute(statement)
        if cur.description:
            names = [d[0] for d in cur.description]
            result_sets.extend(dict(zip(names, row)) for row in cur.fetchall())
    return result_sets


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    load_sample(conn)
    rows = run_sql(conn)
    queries = {row["review_query"] for row in rows}
    assert "duplicate_invoice_number_amount" in queries, rows
    assert "same_day_same_amount" in queries, rows
    assert "credit_cancelled_void_or_refund_marker" in queries, rows
    dup = [r for r in rows if r["review_query"] == "duplicate_invoice_number_amount"]
    assert len(dup) == 1 and dup[0]["vendor_id"] == "V-100" and dup[0]["row_count"] == 2, dup
    assert any(r["vendor_id"] == "V-200" and r["row_count"] == 2 for r in rows), rows
    credit = [r for r in rows if r["review_query"] == "credit_cancelled_void_or_refund_marker"]
    assert len(credit) == 1 and credit[0]["vendor_id"] == "V-300", credit
    print(f"AP_SQL_CHECKS_OK rows={len(rows)} queries={','.join(sorted(queries))} money_verified_eur=0")


if __name__ == "__main__":
    main()
