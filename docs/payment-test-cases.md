# Brightloop Subscription Management System — Payment & Accounting QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Execution (Not Run)
- **Scope:** Dedicated test suite covering payment registration, transaction references, partial payments, multiple installment settlements, overpayments, journal reconciliation, and payment reversal audits.
- **Traceability:** Maps directly to `docs/billing-requirements.md` and `docs/recurring-billing-workflow.md`.

---

## 1. Test Suite Summary

| Category Code | Functional Area | Normal | Boundary | Negative | Permission | Total Test Cases |
|---|---|---|---|---|---|---|
| **TC-PAY-REG** | Payment Registration & Metadata | 2 | 1 | 2 | 1 | 6 |
| **TC-PAY-PART**| Partial & Multiple Payment Settlements | 3 | 2 | 1 | 0 | 6 |
| **TC-PAY-REC** | Accounting Reconciliation & Ledgers | 2 | 2 | 1 | 1 | 6 |
| **TC-PAY-REV** | Payment Reversals, Chargebacks & Refunds| 2 | 1 | 2 | 1 | 6 |
| **Total** | | **9** | **6** | **6** | **3** | **24** |

---

## 2. Detailed Test Cases

### 2.1 Payment Registration & Metadata (TC-PAY-REG)

#### TC-PAY-001 (Normal): Single Invoice Full Payment via Customer Portal
- **Traceability:** REQ-BILL-008, REQ-BILL-016
- **Test Type:** Normal
- **Preconditions:** Posted subscription invoice `INV/2026/00101` for $250.00 in `not_paid` state. Customer logged into portal.
- **Test Data:** Payment amount: $250.00, Payment Gateway: Mock Credit Card.
- **Execution Steps:**
  1. Customer navigates to `/my/invoices/101`.
  2. Clicks "Pay Now".
  3. Enters card credentials and confirms.
- **Expected Result:**
  - Payment transaction captured successfully with external transaction ID.
  - Odoo `account.payment` record created with payment reference `PAY/2026/00101`.
  - Receivable line reconciled against bank journal entry.
  - Invoice status becomes `paid`; residual amount is `$0.00`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-002 (Normal): Backend Manual Wire Payment with Reference and Internal Notes
- **Traceability:** REQ-BILL-008, REQ-BILL-016
- **Test Type:** Normal
- **Preconditions:** Posted subscription invoice `INV/2026/00102` for $1,200.00. Staff user logged in.
- **Test Data:**
  - Bank Journal: `BNK1/USD`
  - Reference: `WIRE-REF-987654`
  - Communication / Memo: `Annual Subscription Payment — Enterprise Tier`
- **Execution Steps:**
  1. Open invoice in backend and click "Register Payment".
  2. Select Bank journal, input Amount $1,200.00, Reference `WIRE-REF-987654`, and Note.
  3. Click "Create Payment".
- **Expected Result:**
  - Payment created with reference stored in `ref` and notes visible in chatter.
  - Invoice `payment_state` becomes `paid`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-003 (Negative): Payment Registration with Invalid Payment Method
- **Traceability:** REQ-BILL-008
- **Test Type:** Negative
- **Preconditions:** Invoice posted.
- **Test Data:** Inactive/archived payment journal.
- **Execution Steps:**
  1. Attempt to register payment selecting an archived payment method via API.
- **Expected Result:** Action blocked; UserError: `"Selected payment method is no longer active. Please select an active payment journal."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.2 Partial & Multiple Payments Against One Invoice (TC-PAY-PART)

#### TC-PAY-004 (Normal): Two-Stage Installment Payment (Partial $\rightarrow$ Full)
- **Traceability:** REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Subscription invoice for $1,000.00 posted.
- **Test Data:** Payment 1: $600.00; Payment 2: $400.00.
- **Execution Steps:**
  1. Register Payment 1 for $600.00.
  2. Inspect invoice `payment_state` and `amount_residual`.
  3. Register Payment 2 for $400.00.
  4. Inspect invoice status.
- **Expected Result:**
  - Step 2: `payment_state` is `partial`; `amount_residual` is `$400.00`.
  - Step 4: `payment_state` transitions to `paid`; `amount_residual` is `$0.00`.
  - Invoice payment widget displays both payment records with timestamps and amounts.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-005 (Boundary): Three Micro-Payments to Settle Single Invoice
- **Traceability:** REQ-BILL-008
- **Test Type:** Boundary
- **Preconditions:** Invoice for $100.00 posted.
- **Test Data:** Payment 1: $33.33; Payment 2: $33.33; Payment 3: $33.34.
- **Execution Steps:**
  1. Register Payment 1 ($33.33) $\rightarrow$ Residual: $66.67.
  2. Register Payment 2 ($33.33) $\rightarrow$ Residual: $33.34.
  3. Register Payment 3 ($33.34) $\rightarrow$ Residual: $0.00.
- **Expected Result:**
  - Each payment increments reconciled amount accurately.
  - Final residual is exactly `$0.00` without 1-cent rounding orphan balance.
  - Status transitions to `paid`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-006 (Negative): Payment Amount of Zero or Negative
- **Traceability:** REQ-BILL-008
- **Test Type:** Negative
- **Preconditions:** Invoice posted.
- **Test Data:** Payment Amount: `$0.00` and `$-50.00`.
- **Execution Steps:**
  1. Attempt to register payment with $0.00.
  2. Attempt to register payment with -$50.00.
- **Expected Result:** Validation error thrown: `"The payment amount must be strictly greater than zero."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.3 Accounting Reconciliation & Ledgers (TC-PAY-REC)

#### TC-PAY-007 (Normal): Multi-Invoice Single Batch Payment Reconciliation
- **Traceability:** REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Customer has 2 open subscription invoices: `INV/001` ($200.00) and `INV/002` ($300.00). Total due: $500.00.
- **Test Data:** Single batch wire transfer payment of $500.00.
- **Execution Steps:**
  1. Register batch payment of $500.00 selecting both invoices.
  2. Reconcile payment lines.
- **Expected Result:**
  - Payment of $500.00 generates one `account.payment`.
  - Both `INV/001` and `INV/002` are fully reconciled and marked `paid`.
  - Customer balance on Accounts Receivable ledger becomes `$0.00`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-008 (Boundary): Customer Overpayment Creating Unallocated Credit Balance
- **Traceability:** REQ-BILL-008
- **Test Type:** Boundary
- **Preconditions:** Invoice for $400.00 posted.
- **Test Data:** Payment remittance of $500.00 ($100.00 excess).
- **Execution Steps:**
  1. Register payment for $500.00 against the $400.00 invoice.
  2. Select "Keep open as customer credit balance" option.
- **Expected Result:**
  - Invoice is reconciled to `$0.00` residual and marked `paid`.
  - Unreconciled credit entry of `$100.00` remains on customer partner ledger.
  - Subsequent month's subscription invoice automatically detects available credit.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.4 Payment Reversals, Chargebacks & Refunds (TC-PAY-REV)

#### TC-PAY-009 (Normal): Payment Unreconcile and Cancellation
- **Traceability:** REQ-BILL-006, REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Invoice `INV/003` was marked `paid` via registered payment `PAY/003`.
- **Test Data:** Customer check bounced.
- **Execution Steps:**
  1. Open payment `PAY/003` and click "Unreconcile".
  2. Cancel payment.
- **Expected Result:**
  - Reconciliation link removed.
  - Invoice `INV/003` reverts to `not_paid` with full residual balance restored.
  - Chatter logs payment cancellation audit trail.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PAY-010 (Normal): Partial Refund Credit Note Generation
- **Traceability:** REQ-BILL-006, REQ-BILL-008
- **Test Type:** Normal
- **Preconditions:** Active subscription invoice paid in full ($500.00). Customer experienced 2-day outage; manager approves $50.00 SLA credit.
- **Test Data:** Partial credit note for $50.00.
- **Execution Steps:**
  1. Open invoice and click "Add Credit Note".
  2. Enter partial amount $50.00 and reason "SLA Outage Credit".
  3. Post credit note.
- **Expected Result:**
  - Credit note `RINV/2026/00001` created for -$50.00.
  - Generates $50.00 customer balance or refund payout.
  - Original subscription contract remains active.
- **Actual Result:** 
- **Status:** Not Run
