#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Iterable, List

COLUMNS = [
    "vendor_id",
    "vendor_name",
    "invoice_number",
    "invoice_date",
    "due_date",
    "payment_date",
    "amount",
    "currency",
    "payment_reference",
    "status",
]

SQL = Path(__file__).resolve().parents[1] / "sql" / "ap_duplicate_payment_checks.sql"


def normalize_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def load_csv(conn: sqlite3.Connection, csv_path: Path) -> int:
    conn.execute("DROP TABLE IF EXISTS ap_export")
    conn.execute(
        """
        CREATE TABLE ap_export (
            vendor_id TEXT, vendor_name TEXT, invoice_number TEXT, invoice_date TEXT,
            due_date TEXT, payment_date TEXT, amount REAL, currency TEXT,
            payment_reference TEXT, status TEXT
        )
        """
    )
    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        missing = [column for column in COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"missing required columns: {', '.join(missing)}")
        rows = [[row.get(column, "") for column in COLUMNS] for row in reader]
    conn.executemany("INSERT INTO ap_export VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    return len(rows)


def run_sql(conn: sqlite3.Connection) -> List[Dict[str, object]]:
    statements = [part.strip() for part in SQL.read_text(encoding="utf-8").split(";") if part.strip()]
    findings: List[Dict[str, object]] = []
    for statement in statements:
        cur = conn.execute(statement)
        if cur.description:
            names = [description[0] for description in cur.description]
            findings.extend(dict(zip(names, row)) for row in cur.fetchall())
    return findings


def write_github_output(values: Dict[str, object]) -> None:
    output_env = str(__import__("os").environ.get("GITHUB_OUTPUT", "")).strip()
    if not output_env:
        return
    output_path = Path(output_env)
    with output_path.open("a", encoding="utf-8") as fh:
        for key, value in values.items():
            safe_key = re.sub(r"[^A-Za-z0-9_-]", "_", key)
            fh.write(f"{safe_key}={value}\n")


def build_report(csv_path: Path, row_count: int, findings: Iterable[Dict[str, object]]) -> Dict[str, object]:
    finding_rows = list(findings)
    by_query: Dict[str, int] = {}
    for row in finding_rows:
        by_query[str(row.get("review_query", "unknown"))] = by_query.get(str(row.get("review_query", "unknown")), 0) + 1
    return {
        "input_file": str(csv_path),
        "rows_reviewed": row_count,
        "findings_count": len(finding_rows),
        "finding_groups_by_query": by_query,
        "findings": finding_rows,
        "safety_note": "Findings are review leads only. Use authorized exports and do not publish confidential vendor, banking, tax, invoice or personal data.",
        "money_verified_eur": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Find duplicate-payment review leads in an authorized AP CSV export.")
    parser.add_argument("csv_path", help="CSV file with the expected AP export columns")
    parser.add_argument("--output", default="ap-duplicate-payment-audit.json", help="Path for the JSON audit report")
    parser.add_argument("--fail-on-findings", default="false", help="Exit 1 when any findings are present: true/false")
    args = parser.parse_args()

    csv_path = Path(args.csv_path).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    row_count = load_csv(conn, csv_path)
    findings = run_sql(conn)
    report = build_report(csv_path, row_count, findings)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_github_output({"findings-count": report["findings_count"], "report-path": output})
    print(f"AP_DUPLICATE_PAYMENT_AUDIT rows={row_count} findings={report['findings_count']} output={output}")
    if report["findings_count"] and normalize_bool(args.fail_on_findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
