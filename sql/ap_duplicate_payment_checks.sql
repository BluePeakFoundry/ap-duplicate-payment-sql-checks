-- AP Duplicate Payment SQL Checks
-- SQLite-compatible starter queries for authorized accounts-payable exports.
-- A finding is a review lead only. It is not proof of overpayment or refund eligibility.

DROP VIEW IF EXISTS normalized_ap_export;
CREATE TEMP VIEW normalized_ap_export AS
SELECT
  vendor_id,
  vendor_name,
  invoice_number,
  invoice_date,
  due_date,
  payment_date,
  ROUND(CAST(amount AS REAL), 2) AS amount_key,
  CAST(amount AS REAL) AS amount,
  currency,
  payment_reference,
  status,
  LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(TRIM(COALESCE(invoice_number, '')), '-', ''), ' ', ''), '/', ''), '.', ''), '#', '')) AS invoice_number_key
FROM ap_export;

SELECT
  'duplicate_invoice_number_amount' AS review_query,
  vendor_id,
  vendor_name,
  invoice_number_key,
  NULL AS invoice_date,
  currency,
  amount_key,
  COUNT(*) AS row_count,
  GROUP_CONCAT(COALESCE(payment_reference, '[no payment reference]'), ', ') AS references_or_statuses
FROM normalized_ap_export
WHERE invoice_number_key <> ''
GROUP BY vendor_id, vendor_name, invoice_number_key, currency, amount_key
HAVING COUNT(*) > 1;

SELECT
  'same_day_same_amount' AS review_query,
  vendor_id,
  vendor_name,
  NULL AS invoice_number_key,
  invoice_date,
  currency,
  amount_key,
  COUNT(*) AS row_count,
  GROUP_CONCAT(COALESCE(invoice_number, '[no invoice number]'), ', ') AS references_or_statuses
FROM normalized_ap_export
GROUP BY vendor_id, vendor_name, invoice_date, currency, amount_key
HAVING COUNT(*) > 1;

SELECT
  'credit_cancelled_void_or_refund_marker' AS review_query,
  vendor_id,
  vendor_name,
  invoice_number_key,
  invoice_date,
  currency,
  amount_key,
  COUNT(*) AS row_count,
  GROUP_CONCAT(COALESCE(status, '[no status]'), ', ') AS references_or_statuses
FROM normalized_ap_export
WHERE LOWER(COALESCE(status, '')) LIKE '%credit%'
   OR LOWER(COALESCE(status, '')) LIKE '%cancel%'
   OR LOWER(COALESCE(status, '')) LIKE '%void%'
   OR LOWER(COALESCE(status, '')) LIKE '%refund%'
   OR amount_key < 0
GROUP BY vendor_id, vendor_name, invoice_number_key, invoice_date, currency, amount_key;
