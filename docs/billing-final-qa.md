# Brightloop Subscription Management System — Billing & Accounting Final Acceptance QA

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Acceptance Ready (Not Run)
- **Role:** Final QA Documentation & Acceptance Testing
- **Module:** `brightloop_billing`
- **Target ERP Platform:** Odoo 19

---

## Acceptance Test Protocol

For each test case below, the lead developer must execute the test in a running Odoo 19 instance, record the actual result, update the status (`Passed` or `Failed`), and attach the specified verification evidence.

---

### Test Case: ACC-BILL-001 — Automated Recurring Invoice Generation & Next Date Rollover
- **Preconditions:** Active monthly subscription (`SUB/2026/01001`) with start date `2026-10-01`, `next_invoice_date = '2026-11-01'`. Current system date set to `2026-11-01`.
- **Test Data:** Customer: `Acme Industrial Ltd`, Product: `Cloud Security Pro` (10 seats @ $50/mo = $500).
- **Steps:**
  1. Navigate to Settings > Technical > Scheduled Actions.
  2. Locate `Subscription: Generate Invoices` and click "Run Manually".
  3. Navigate to Invoicing > Customers > Invoices.
  4. Open newly generated invoice.
  5. Check `SUB/2026/01001` form view for updated `next_invoice_date`.
- **Expected Result:**
  - One customer invoice generated for $500.00 with invoice date `2026-11-01`.
  - Invoice lines specify coverage: `"Cloud Security Pro - Coverage: 2026-11-01 to 2026-11-30"`.
  - Origin subscription `next_invoice_date` is updated to `2026-12-01`.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of generated invoice header + screenshot of updated subscription form view.

---

### Test Case: ACC-BILL-002 — Duplicate Invoice Creation Prevention Guard
- **Preconditions:** Invoice `INV/2026/00045` already exists and is posted for `SUB/2026/01001` covering period `2026-11-01` to `2026-11-30`.
- **Test Data:** Subscription `SUB/2026/01001`.
- **Steps:**
  1. Open subscription form in backend.
  2. Click "Generate Invoice" button manually while system date is still `2026-11-01`.
- **Expected Result:** System blocks action; displays warning dialog: `"An invoice has already been generated for this subscription period (INV/2026/00045)."`; no duplicate invoice record created.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of warning dialog + database query output showing `count(*) = 1` for `(subscription_id, period_start_date, period_end_date)`.

---

### Test Case: ACC-BILL-003 — Multi-Tax Computation & Fiscal Position Mapping
- **Preconditions:** Customer configured with California Tax Fiscal Position (State 6.0% + County 1.25% + District 1.0% = 8.25% total).
- **Test Data:** Subtotal: $1,000.00.
- **Steps:**
  1. Generate subscription invoice for California customer.
  2. Inspect invoice tax summary table.
- **Expected Result:**
  - Untaxed Amount: `$1,000.00`
  - Tax Lines: CA State Tax ($60.00), County Tax ($12.50), District Tax ($10.00)
  - Total Tax: `$82.50`
  - Total Amount: `$1,082.50`
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** PDF printout of invoice showing itemized tax breakdown.

---

### Test Case: ACC-BILL-004 — Full Payment Registration and Automatic Reconciliation
- **Preconditions:** Posted invoice `INV/2026/00050` for $1,082.50 in `not_paid` state.
- **Test Data:** Payment amount: $1,082.50 via Bank Wire.
- **Steps:**
  1. Click "Register Payment".
  2. Select Bank journal, Amount $1,082.50, Payment Reference `WIRE-9921`.
  3. Click "Create Payment".
- **Expected Result:**
  - `account.payment` record created and posted.
  - Invoice `payment_state` becomes `paid`.
  - Amount Residual becomes `$0.00`.
  - Payment ribbon "PAID" displayed in green on top-right of form.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of invoice showing green PAID ribbon and reconciled payment widget.

---

### Test Case: ACC-BILL-005 — Partial Payment Residual Tracking & Dunning Status
- **Preconditions:** Posted invoice for $1,000.00 with payment terms Net 15.
- **Test Data:** Partial payment of $350.00.
- **Steps:**
  1. Register payment for $350.00.
  2. Inspect invoice `payment_state` and `amount_residual`.
  3. Advance system clock past due date.
- **Expected Result:**
  - Invoice status is `partial`.
  - Residual balance is `$650.00`.
  - Once due date passes, invoice appears in Overdue Aging bucket with residual `$650.00` (not full $1,000.00).
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of invoice partial payment banner + Aged Receivable partner ledger line.
