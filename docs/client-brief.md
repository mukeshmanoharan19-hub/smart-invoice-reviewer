# Client brief

## The company

Northstar Facilities Pvt. Ltd. is a fictional facilities-management company based in Bengaluru. It buys cleaning, maintenance, electrical, plumbing, and equipment services from suppliers across India.

Maya works in finance and administration. Supplier invoices and employee expense receipts arrive as digital PDFs, scans, screenshots, and phone photos. They may be written in English, Hindi, Tamil, or Marathi. Before a document enters bookkeeping, Maya needs to know what it is, confirm the important values, check GSTIN and totals, and assign the correct account.

All product copy, source code, documentation, and teaching content is English. Only the example supplier documents vary in language.

## User story

> As a finance administrator at an Indian company, I want to upload a multilingual invoice or receipt and receive a prepared review containing the best combined extraction, GSTIN and policy results, and a suggested GL account so I can approve valid documents quickly and turn supplier errors into a clear correction request.

## What's included in the build

- One PDF or image per upload, with a 4 MB limit.
- Automatic invoice/receipt recognition with strict OpenAI structured output.
- A single OpenAI extraction of the uploaded PDF/PNG/JPEG into provider-independent fields.
- Invoice supplier/customer details and GSTINs, dates, PO, currency, and totals.
- Receipt merchant, transaction date, expense category, subtotal, tax, and total.
- Offline Indian GSTIN format/checksum validation plus receipt tax-total reconciliation.
- Separate deterministic invoice and receipt policies, duplicate detection, corrections, approval, and rejection.
- A fixed Northstar GL catalog plus an OpenAI structured suggestion that a reviewer can override.
- SQLite, local file storage, and a guided welcome → upload/preview → process → review flow.
- Review history with explicit local deletion so the same invoice can be demonstrated again.
- An on-demand OpenAI correction-email draft with Copy and Close; the app never sends it.
- Sample PDFs under `samples/generated/` for manual demos. Bring your own receipt image to exercise the receipt path.

## Northstar policy

The Northstar policy is simply the fictional company's rulebook expressed as ordinary Python. It decides what must be fixed before approval; OpenAI extracts evidence, but it does not own these rules.

### Invoice rules

Errors block approval: missing vendor/customer identity, missing or malformed supplier GSTIN, missing/mismatched customer GSTIN, missing invoice number/date/total/currency, non-positive total, invalid date order, total mismatch over INR 0.01, and duplicate vendor/invoice keys. Missing PO and self-reported extraction confidence below 0.80 are warnings.

### Receipt rules

A receipt records an expense that was already paid, so it does not need an invoice number, customer GSTIN, PO, or due date. Merchant, transaction date, currency, positive total, and tax total are required. When subtotal and tax are present, they must reconcile to the total within INR 0.01. Low self-reported confidence is a warning.

A valid selected Northstar GL account is also required for approval. The model may suggest one, but Maya remains responsible for the selection.

An LLM value is evidence only. It cannot validate GSTIN, reconcile totals, or decide approval. Maya sees the prepared review and makes the call.
