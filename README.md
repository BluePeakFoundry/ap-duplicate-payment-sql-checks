# AP Duplicate Payment SQL Checks

A small, privacy-first starter kit for finding duplicate or suspicious accounts-payable payments in exported ledger data.

Use it on your own authorized exports only. Do not paste supplier contracts, bank details, tax identifiers, account numbers, personal data, invoice images, or confidential vendor information into public systems.

## What is included

- `sql/ap_duplicate_payment_checks.sql` — portable SQLite queries for common review patterns.
- `sample/sample_ap_export.csv` — synthetic sample data for testing the queries.
- `tests/run_checks.py` — local test runner that imports the sample into SQLite and verifies expected findings.
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
```

## Columns expected

The sample and SQL expect: `vendor_id`, `vendor_name`, `invoice_number`, `invoice_date`, `due_date`, `payment_date`, `amount`, `currency`, `payment_reference`, `status`.

Rename columns in your export or adjust the `ap_export` table definition before running the checks.

## License

MIT.
