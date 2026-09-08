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
    action = (ROOT / "action.yml").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "audit_duplicate_payments.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ap-duplicate-payment-audit.yml").read_text(encoding="utf-8")
    for text_name, text in [("index", html), ("readme", readme), ("sql", sql), ("action", action), ("script", script), ("workflow", workflow)]:
        for forbidden in FORBIDDEN:
            require(not re.search(rf"\b{re.escape(forbidden)}\b", text, re.IGNORECASE), f"forbidden term {forbidden!r} in {text_name}")
    require("bluepeakfoundry.goatcounter.com/count" in html, "missing GoatCounter script")
    require('data-analytics-event="download:ap-sql"' in html, "missing download event marker")
    require('data-analytics-event="action:ap-csv-audit"' in html, "missing action event marker")
    require('data-analytics-event="usecase:ap-review"' in html, "missing AP review use-case event marker")
    require('data-analytics-event="download:ap-use-case-sql"' in html, "missing AP use-case download event marker")
    require('data-analytics-event="lead:ap-use-case-scope"' in html, "missing AP use-case scope event marker")
    require('data-analytics-event="lead:ap-sql-review"' in html, "missing review lead event marker")
    require('data-analytics-event="lead:ap-service-scope"' in html, "missing service-scope lead event marker")
    require("ap-sql-review.yml" in html, "missing AP SQL review issue form link")
    require("ap-service-scope.yml" in html, "missing AP service-scope issue form link")
    issue_form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "ap-sql-review.yml").read_text(encoding="utf-8")
    issue_form_lower = issue_form.lower()
    require("do not post supplier names" in issue_form_lower, "issue form missing data-safety warning")
    require("confidential vendor information" in issue_form_lower, "issue form missing confidential-data warning")
    service_form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "ap-service-scope.yml").read_text(encoding="utf-8")
    service_form_lower = service_form.lower()
    require("sanitized service" in service_form_lower, "service form missing sanitized-scope wording")
    require("does not create a contract" in service_form_lower, "service form missing no-contract wording")
    require("guarantee a refund" in service_form_lower, "service form missing no-refund-guarantee wording")
    require("confidential vendor information" in service_form_lower, "service form missing confidential-data warning")
    require("SoftwareSourceCode" in html, "missing structured data")
    require("https://bluepeakfoundry.github.io/ap-duplicate-payment-sql-checks/" in html, "missing canonical URL")
    require("ap_duplicate_payment_checks.sql" in readme, "README missing SQL file reference")
    require("AP Duplicate Payment CSV Audit" in action, "action metadata missing name")
    require("runs:" in action and "using: 'composite'" in action, "action metadata missing composite run block")
    require("csv-path" in action and "findings-count" in action, "action metadata missing inputs/outputs")
    require("BluePeakFoundry/ap-duplicate-payment-sql-checks@v0.2.1-marketplace-ready" in readme, "README missing action usage")
    require("Common AP review use cases" in readme, "README missing AP use-case section")
    require("NetSuite, SAP, Oracle, QuickBooks" in html, "HTML missing ERP use-case keywords")
    require("findings-count" in html and "report-path" in html, "HTML missing action output names")
    require("published_action_release_with_inputs_outputs_docs" in manifest.get("external_actions_performed", []), "manifest missing action docs release marker")
    require("AP_DUPLICATE_PAYMENT_AUDIT" in script, "audit script missing success marker")
    require("examples/invoices.csv" in workflow, "example workflow missing synthetic CSV")
    require(manifest.get("money_verified_eur") == 0, "manifest money field invalid")
    require("published_marketplace_compatible_github_action" in manifest.get("external_actions_performed", []), "manifest missing action external action")
    require("published_sanitized_ap_service_scope_cta" in manifest.get("external_actions_performed", []), "manifest missing service-scope CTA marker")
    require("published_ap_review_use_case_landing_path" in manifest.get("external_actions_performed", []), "manifest missing AP use-case landing path marker")
    print(f"AP_SQL_PUBLIC_SITE_OK files=15 money_verified_eur=0 external_actions={len(manifest.get('external_actions_performed', []))}")


if __name__ == "__main__":
    main()
