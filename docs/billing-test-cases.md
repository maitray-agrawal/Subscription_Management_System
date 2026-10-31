# Brightloop Subscription Management System — Billing, Payment & Accounting QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Execution (Not Run)
- **Scope:** Normal, Boundary, Negative, and Permission verification covering recurring invoice generation, duplicate prevention, tax calculation, payment reconciliation, dunning aging, and cancellation/reversals.
- **Traceability:** Directly maps to `docs/billing-requirements.md`.

---

## 1. Test Suite Summary

| Category Code | Functional Area | Normal | Boundary | Negative | Permission | Total Test Cases |
|---|---|---|---|---|---|---|
| **TC-REC** | Recurring Invoice Generation & Schedules | 2 | 3 | 2 | 1 | 8 |
| **TC-DUP** | Duplicate Prevention & Idempotency | 1 | 1 | 2 | 0 | 4 |
| **TC-TAX** | Tax Handling (Exclusive & Inclusive) | 2 | 2 | 1 | 1 | 6 |
| **TC-PAY** | Payment Processing & Accounting | 3 | 2 | 2 | 1 | 8 |
| **TC-DUE** | Due Dates, Overdue & Dunning | 2 | 2 | 1 | 1 | 6 |
| **TC-REV** | Payment & Invoice Reversals / Credit Notes | 2 | 1 | 2 | 1 | 6 |
| **Total** | | **12** | **11** | **10** | **5** | **38** |

---

## 2. Test Cases

### 2.1 Recurring Invoicing & Billing Schedules (TC-REC)

#### TC-REC-001 (Normal): Monthly Recurring Invoice Generation on Due Date
- **Traceability:** REQ-BILL-001, REQ-BILL-002, REQ-BILL-003
- **Test Type:** Normal
- **Preconditions:** Active monthly subscription (`SUB/2026/001`) with start date `2026-10-01`, `next_invoice_date = '2026-11-01'`. Current system date: `2026-11-01`.
- **Test Data:** 10 seats @ $20.00/month = $200.00.
- **Execution Steps:**
  1. Trigger automated recurring invoice cron (`ir.cron_generate_subscription_invoices`).
  2. Inspect subscription `SUB/2026/001`.
  3. Inspect generated invoice `account.move`.
- **Expected Result:**
  - One new customer invoice generated with invoice date `2026-11-01`.
  - Line items match subscription lines (10 seats @ $20 = $200).
  - Invoice linked to `SUB/2026/001`.
  - Subscription `next_invoice_date` advances to `2026-12-01`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REC-002 (Boundary): Leap Year End-of-Month Rollover (Jan 31 -> Feb 29 -> Mar 31)
- **Traceability:** REQ-BILL-002
- **Test Type:** Boundary
- **Preconditions:** Subscription created with anchor date `2028-01-31` (2028 is a leap year). Monthly billing cadence.
- **Test Data:** Anchor day: 31.
- **Execution Steps:**
  1. Set system date to `2028-01-31`, trigger invoice 1 $\rightarrow$ verify next invoice date.
  2. Set system date to `2028-02-29`, trigger invoice 2 $\rightarrow$ verify next invoice date.
  3. Set system date to `2028-03-31`, trigger invoice 3 $\rightarrow$ verify next invoice date.
- **Expected Result:**
  - Cycle 1 next date = `2028-02-29` (clamped to end of February).
  - Cycle 2 next date = `2028-03-31` (retains anchor day 31, does not stick to 29th).
  - Cycle 3 next date = `2028-04-30` (clamped to 30 days).
- **Actual Result:** 
- **Status:** Not Run

#### TC-REC-003 (Boundary): Non-Leap Year End-of-Month Rollover (Jan 31 -> Feb 28)
- **Traceability:** REQ-BILL-002
- **Test Type:** Boundary
- **Preconditions:** Subscription created on `2027-01-31` (Non-leap year).
- **Test Data:** Anchor day: 31.
- **Execution Steps:**
  1. Trigger cycle 1 billing.
- **Expected Result:** Next billing date is set exactly to `2027-02-28`. Subsequent cycle sets to `2027-03-31`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REC-004 (Normal): Missed Billing Cycle Catch-Up After Outage
- **Traceability:** REQ-BILL-005
- **Test Type:** Normal
- **Preconditions:** Server outage prevented cron from running between `2026-10-01` and `2026-12-05`. Subscription had `next_invoice_date = '2026-10-01'`. Current date: `2026-12-05`.
- **Test Data:** Monthly subscription @ $100/mo.
- **Execution Steps:**
  1. Run recurring invoice cron.
- **Expected Result:**
  - System generates 3 distinct invoices: Cycle 1 (Oct 1 - Oct 31), Cycle 2 (Nov 1 - Nov 30), Cycle 3 (Dec 1 - Dec 31).
  - No billing periods skipped.
  - `next_invoice_date` updated to `2027-01-01`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REC-005 (Negative): Invoicing Skipped for Paused Subscription
- **Traceability:** REQ-BILL-003
- **Test Type:** Negative
- **Preconditions:** Active subscription with `is_paused = True`, pause date `2026-10-15`, `next_invoice_date = '2026-11-01'`. Current system date: `2026-11-01`.
- **Test Data:** Paused subscription record.
- **Execution Steps:**
  1. Run daily billing cron.
- **Expected Result:** Subscription is bypassed; zero invoices generated; `next_invoice_date` remains unchanged.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.2 Duplicate Prevention & Idempotency (TC-DUP)

#### TC-DUP-001 (Boundary): Rapid Concurrent Cron & Manual Invoice Generation
- **Traceability:** REQ-BILL-004
- **Test Type:** Boundary / Stress
- **Preconditions:** Subscription due for billing today (`next_invoice_date = today`).
- **Test Data:** Subscription `SUB/2026/00088`.
- **Execution Steps:**
  1. Fire automated cron in background worker.
  2. Concurrently simulate staff clicking "Generate Invoice" button in UI within the same sub-second window.
- **Expected Result:** Exactly one invoice is generated and persisted; second request acquires lock, detects existing invoice for period `[today, today + 1 month]`, and terminates safely without raising uncaught crash or creating duplicate.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DUP-002 (Negative): Manual Invoice Generation When Unpaid Draft Exists
- **Traceability:** REQ-BILL-004, REQ-BILL-006
- **Test Type:** Negative
- **Preconditions:** A draft invoice already exists for the current subscription billing period.
- **Test Data:** Existing draft invoice `INV/2026/00010`.
- **Execution Steps:**
  1. Staff opens subscription and clicks "Generate Invoice".
- **Expected Result:** Action blocked; user alerted: `"An invoice has already been generated for this billing period (INV/2026/00010). Please post or cancel the existing invoice before generating a new one."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.3 Tax Handling (Exclusive & Inclusive) (TC-TAX)

#### TC-TAX-001 (Normal): Tax-Exclusive Pricing (B2B Standard 20% VAT)
- **Traceability:** REQ-BILL-007
- **Test Type:** Normal
- **Preconditions:** Tax-exclusive product configured @ $100.00. Tax rate: 20% VAT (Price excluded from tax).
- **Test Data:** Quantity: 5 units. Subtotal = $500.00.
- **Execution Steps:**
  1. Generate subscription invoice.
  2. Inspect invoice line and totals.
- **Expected Result:**
  - Untaxed Amount: `$500.00`
  - Tax Amount: `$100.00` ($500 \times 0.20$)
  - Total Amount: `$600.00`
- **Actual Result:** 
- **Status:** Not Run

#### TC-TAX-002 (Normal): Tax-Inclusive Pricing (B2C Retail 10% GST)
- **Traceability:** REQ-BILL-007
- **Test Type:** Normal
- **Preconditions:** Tax-inclusive product configured @ $110.00 (Price included in tax). Tax rate: 10% GST.
- **Test Data:** Quantity: 2 units. Total Gross = $220.00.
- **Execution Steps:**
  1. Generate subscription invoice.
  2. Inspect invoice totals.
- **Expected Result:**
  - Untaxed Amount: `$200.00` ($\$220.00 / 1.10$)
  - Tax Amount: `$20.00` ($\$220.00 - \$200.00$)
  - Total Gross Amount: `$220.00`
- **Actual Result:** 
- **Status:** Not Run

#### TC-TAX-003 (Boundary): Multi-Tax Calculation and Fractional Cent Rounding
- **Traceability:** REQ-BILL-007
- **Test Type:** Boundary
- **Preconditions:** Dual taxes: State Tax 6.25% + City Tax 2.5% (Total 8.75%). Currency: USD (rounding 0.01).
- **Test Data:** Line 1: 1 unit @ $33.33. Line 2: 1 unit @ $66.67.
- **Execution Steps:**
  1. Calculate line taxes and total invoice amount.
- **Expected Result:**
  - Untaxed: `$100.00` ($33.33 + $66.67)
  - State Tax (6.25%): `$6.25`
  - City Tax (2.5%): `$2.50`
  - Total Tax: `$8.75`
  - Total Amount: `$108.75` (Half-up rounding preserves exact balance without 1-cent discrepancy).
- **Actual Result:** 
- **Status:** Not Run

---

### 2.4 Payment Processing & Accounting (TC-PAY)

#### TC-PAY-001 (Normal): Full Payment Registration and Reconciliation
- **Traceability:** REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Posted invoice `INV/2026/00100` for $500.00 in `not_paid` state.
- **Test Data:** Payment amount: $500.00 via Bank Transfer.
- **Execution Steps:**
  1. Open invoice and click "Register Payment".
  2. Select Journal: Bank, Amount: $500.00, Date: Today.
  3. Click "Create Payment".
- **Expected Result:**
  - Payment record created in `account.payment`.
  - Receivable move line reconciled against invoice move line.
  - Invoice `payment_state` becomes `paid`.
  - Invoice residual amount becomes `$0.00`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-002 (Normal): Partial Payment Registration
- **Traceability:** REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Posted invoice for $1,000.00.
- **Test Data:** Partial payment of $400.00.
- **Execution Steps:**
  1. Register payment for $400.00.
  2. Inspect invoice state.
- **Expected Result:**
  - Invoice `payment_state` becomes `partial`.
  - Residual amount (`amount_residual`) updates to `$600.00`.
  - Partial payment banner displayed on invoice view.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-003 (Boundary): Multiple Consecutive Partial Payments to Full Settlement
- **Traceability:** REQ-BILL-008
- **Test Type:** Boundary
- **Preconditions:** Invoice for $1,000.00 partially paid with $400.00 (Residual $600.00).
- **Test Data:** Payment 2: $350.00. Payment 3: $250.00.
- **Execution Steps:**
  1. Register Payment 2 ($350.00) $\rightarrow$ inspect residual.
  2. Register Payment 3 ($250.00) $\rightarrow$ inspect status.
- **Expected Result:**
  - After Payment 2: residual is `$250.00`, status is `partial`.
  - After Payment 3: residual is `$0.00`, status transitions to `paid`.
  - All 3 payments visible in invoice payment widget audit trail.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-004 (Boundary): Customer Overpayment Handling
- **Traceability:** REQ-BILL-008
- **Test Type:** Boundary
- **Preconditions:** Posted invoice for $500.00.
- **Test Data:** Customer remits wire payment of $600.00 ($100 overpayment).
- **Execution Steps:**
  1. Register payment of $600.00 against the $500.00 invoice.
  2. Select "Keep open as customer credit balance" option.
- **Expected Result:**
  - Invoice is marked `paid` with residual `$0.00`.
  - Unallocated `$100.00` credit is retained on customer account (`res.partner`) for allocation against future subscription billing.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.5 Due Dates, Overdue & Dunning (TC-DUE)

#### TC-DUE-001 (Normal): Overdue Aging Classification
- **Traceability:** REQ-BILL-009, REQ-BILL-010
- **Test Type:** Normal
- **Preconditions:** Invoice posted on Oct 1 with Net 15 payment terms (`invoice_date_due = '2026-10-16'`).
- **Test Data:** Simulated current dates: Oct 10 (Current), Oct 20 (Late 1-15), Nov 05 (Overdue 16-30).
- **Execution Steps:**
  1. Check invoice aging on Oct 10.
  2. Check invoice aging on Oct 20.
  3. Check invoice aging on Nov 05.
- **Expected Result:**
  - Oct 10: Marked `Current` (0 days overdue).
  - Oct 20: Marked `Overdue` (4 days overdue, Bucket: Late 1-15).
  - Nov 05: Marked `Overdue` (20 days overdue, Bucket: Overdue 16-30).
- **Actual Result:** 
- **Status:** Not Run

#### TC-DUE-002 (Normal): Automated Dunning Retry Schedule (Day 1, 3, 7)
- **Traceability:** REQ-BILL-011, REQ-BILL-012
- **Test Type:** Normal
- **Preconditions:** Payment gateway token charge fails with soft decline code `INSUFFICIENT_FUNDS`.
- **Test Data:** Invoice for $250.00.
- **Execution Steps:**
  1. Simulate initial charge failure on Day 0.
  2. Advance system clock to Day 1 and run retry cron.
  3. Advance system clock to Day 3 and run retry cron.
  4. Advance system clock to Day 7 and run retry cron.
- **Expected Result:**
  - System logs 3 distinct retry attempts with timestamps in chatter.
  - Customer receives automated payment retry notices.
  - Invoice remains `posted` and `not_paid`.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.6 Reversals & Invoice Cancellations (TC-REV)

#### TC-REV-001 (Normal): Payment Reversal / Chargeback Handling
- **Traceability:** REQ-BILL-006, REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Invoice `INV/2026/00200` marked `paid` via registered payment.
- **Test Data:** Bank notifies chargeback / bounced check for the payment.
- **Execution Steps:**
  1. Open payment record and click "Unreconcile" / "Cancel Payment".
  2. Inspect invoice status.
- **Expected Result:**
  - Payment is unlinked/canceled.
  - Invoice `payment_state` automatically reverts from `paid` to `not_paid`.
  - Residual amount is restored to original full invoice value.
  - Chatter logs payment reversal audit event.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REV-002 (Normal): Posted Invoice Cancellation via Credit Note
- **Traceability:** REQ-BILL-006
- **Test Type:** Normal
- **Preconditions:** Posted invoice `INV/2026/00300` for $300.00 generated in error.
- **Test Data:** Reversal reason: "Billing correction".
- **Execution Steps:**
  1. Click "Add Credit Note" on posted invoice.
  2. Select "Reverse and Create Draft Credit Note" or "Full Reverse".
  3. Post credit note.
- **Expected Result:**
  - Reversal move `RINV/2026/XXXXX` generated with negative credit entries.
  - Credit note automatically reconciles against origin invoice.
  - Both original invoice and credit note marked `reversed` / `paid`.
- **Actual Result:** 
- **Status:** Not Run
