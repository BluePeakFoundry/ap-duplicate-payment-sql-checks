#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORBIDDEN = ["Sergi", "Rex", "agent", "bot", "money verified", "internal monetization"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    sql = (ROOT / "sql" / "ap_duplicate_payment_checks.sql").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    for text_name, text in [("index", html), ("readme", readme), ("sql", sql)]:
        for forbidden in FORBIDDEN:
            require(not re.search(rf"\b{re.escape(forbidden)}\b", text, re.IGNORECASE), f"forbidden term {forbidden!r} in {text_name}")
    require("bluepeakfoundry.goatcounter.com/count" in html, "missing GoatCounter script")
    require('data-analytics-event="download:ap-sql"' in html, "missing download event marker")
    require('data-analytics-event="lead:ap-sql-review"' in html, "missing review lead event marker")
    require("ap-sql-review.yml" in html, "missing AP SQL review issue form link")
    issue_form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "ap-sql-review.yml").read_text(encoding="utf-8")
    issue_form_lower = issue_form.lower()
    require("do not post supplier names" in issue_form_lower, "issue form missing data-safety warning")
    require("confidential vendor information" in issue_form_lower, "issue form missing confidential-data warning")
    require("SoftwareSourceCode" in html, "missing structured data")
    require("https://bluepeakfoundry.github.io/ap-duplicate-payment-sql-checks/" in html, "missing canonical URL")
    require("ap_duplicate_payment_checks.sql" in readme, "README missing SQL file reference")
    require(manifest.get("money_verified_eur") == 0, "manifest money field invalid")
    require(manifest.get("external_actions_performed") == ["published_public_github_repo", "published_github_pages", "published_github_release", "published_safe_public_issue_form_cta"], "unexpected external actions")
    print("AP_SQL_PUBLIC_SITE_OK files=10 money_verified_eur=0 external_actions=4")


if __name__ == "__main__":
    main()
