# AP Duplicate Payment SQL Checks

A small, privacy-first starter kit for finding duplicate or suspicious accounts-payable payments in exported ledger data.

Use it on your own authorized exports only. Do not paste supplier contracts, bank details, tax identifiers, account numbers, personal data, invoice images, or confidential vendor information into public systems.

## What is included

- `sql/ap_duplicate_payment_checks.sql` — portable SQLite queries for common review patterns.
- `sample/sample_ap_export.csv` — synthetic sample data for testing the queries.
- `tests/run_checks.py` — local test runner that imports the sample into SQLite and verifies expected findings.
- `scripts/audit_duplicate_payments.py` — CSV audit runner that writes a JSON report for local use or CI.
- `action.yml` — GitHub Action metadata for running the CSV audit in a workflow.
- `examples/invoices.csv` — synthetic workflow sample for the action.
- `index.html` — public documentation page for GitHub Pages.
- `.github/ISSUE_TEMPLATE/ap-sql-review.yml` — sanitized public feedback form for false positives, missing patterns and portability notes.

## Review patterns

1. Same vendor + normalized invoice number + currency + amount appears more than once.
2. Same vendor + invoice date + currency + amount appears more than once.
3. Paid rows with credit, cancelled, void or refund status markers, or negative amounts.

These checks produce review leads, not proof of overpayment or entitlement to a refund. Review results manually before contacting any supplier.

## Safe feedback

Use the public feedback form only for sanitized examples and generalized column names:
https://github.com/BluePeakFoundry/ap-duplicate-payment-sql-checks/issues/new?template=ap-sql-review.yml

Do not post supplier names, bank details, tax IDs, account numbers, payment references, invoice images, contracts, personal data or confidential vendor information.

## Run locally

```bash
python3 tests/run_checks.py
python3 scripts/audit_duplicate_payments.py examples/invoices.csv --output artifacts/sample-audit.json
```

The JSON report contains review-lead groups and a safety note. It does not prove overpayment and should be reviewed manually before any supplier contact.

## Use as a GitHub Action

```yaml
name: AP duplicate payment audit
on: workflow_dispatch
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: BluePeakFoundry/ap-duplicate-payment-sql-checks@v0.2.0-csv-audit-action
        with:
          csv-path: examples/invoices.csv
          output-path: artifacts/ap-audit.json
          fail-on-findings: 'false'
```

Use authorized, sanitized exports only. Do not commit live supplier, banking, tax, invoice, account, personal or confidential information to a repository.

## Columns expected

The sample and SQL expect: `vendor_id`, `vendor_name`, `invoice_number`, `invoice_date`, `due_date`, `payment_date`, `amount`, `currency`, `payment_reference`, `status`.

Rename columns in your export or adjust the `ap_export` table definition before running the checks.

## License

MIT.
