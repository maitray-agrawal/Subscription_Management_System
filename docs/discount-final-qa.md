# Brightloop Subscription Management System — Discount Engine Final Acceptance QA

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Acceptance Ready (Not Run)
- **Role:** Final QA Documentation & Acceptance Testing
- **Module:** `brightloop_discount`
- **Target ERP Platform:** Odoo 19

---

## Acceptance Test Protocol

For each test case below, the lead developer must execute the test in a running Odoo 19 instance, record the actual result, update the status (`Passed` or `Failed`), and attach the specified verification evidence.

---

### Test Case: ACC-DISC-001 — Percentage Discount on Subscription Line
- **Preconditions:** Active product `Enterprise Hosting` ($200/mo). Discount code `SAVE20` (20% off).
- **Test Data:** 5 units @ $200 = $1,000.
- **Steps:**
  1. Create subscription quotation for 5 units of `Enterprise Hosting`.
  2. Input discount code `SAVE20` and click "Apply".
  3. Validate quote and generate invoice.
- **Expected Result:**
  - Base Amount: `$1,000.00`
  - Discount Amount: `-$200.00`
  - Untaxed Total: `$800.00`
  - Discount line explicitly itemized with rule name `SAVE20`.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of quotation lines showing 20% discount calculation and invoice totals.

---

### Test Case: ACC-DISC-002 — Fixed Amount Bottom-Line Discount
- **Preconditions:** Subscription order subtotal of $500.00. Promotional rule `FLAT50` ($50.00 fixed deduction).
- **Test Data:** Subtotal: $500.00.
- **Steps:**
  1. Add `FLAT50` to subscription quotation.
  2. Confirm quote and generate invoice.
- **Expected Result:**
  - Dedicated discount line created for `-$50.00`.
  - Net invoice total calculated as `$450.00`.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** PDF invoice showing negative deduction line.

---

### Test Case: ACC-DISC-003 — Expiration Date Boundary Enforcement
- **Preconditions:** Promo code `FALLPROMO` configured with validity date ending `2026-10-31 23:59:59`. System simulated clock: `2026-11-01 00:05:00`.
- **Test Data:** Promo code `FALLPROMO`.
- **Steps:**
  1. Open subscription quotation on Nov 1.
  2. Attempt to apply promo code `FALLPROMO`.
- **Expected Result:** Application rejected; warning toast appears: `"The promotional code 'FALLPROMO' has expired."` No discount applied.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of warning validation toast and un-discounted order lines.

---

### Test Case: ACC-DISC-004 — Global Usage Limit Cap Enforcement
- **Preconditions:** Promotional campaign `LIMITED10` capped at 10 total redemptions. Current redemption counter is at 10.
- **Test Data:** Customer attempt to redeem 11th instance.
- **Steps:**
  1. Enter coupon code `LIMITED10` in portal subscription checkout.
  2. Click "Apply".
- **Expected Result:** System blocks redemption; displays message: `"This promotional voucher has reached its maximum usage limit."`
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of error notice + database query verifying `total_redemptions_count = 10`.

---

### Test Case: ACC-DISC-005 — Introductory Pricing Cycle Exhaustion (3-Month Duration)
- **Preconditions:** Monthly subscription with introductory discount `FIRST3MONTHS` (50% off, `max_cycles = 3`).
- **Test Data:** Cycles 1, 2, 3, and 4 monthly invoice generation.
- **Steps:**
  1. Post Invoice for Cycle 1 $\rightarrow$ check amount and `cycles_applied_count`.
  2. Post Invoice for Cycle 2 $\rightarrow$ check amount.
  3. Post Invoice for Cycle 3 $\rightarrow$ check amount.
  4. Post Invoice for Cycle 4 $\rightarrow$ check amount.
- **Expected Result:**
  - Cycles 1, 2, 3 billed at 50% discount ($50.00 each).
  - Cycle 4 invoice automatically reverts to standard catalog price ($100.00).
  - Chatter logs notice: `"Introductory discount completed its 3-cycle duration."`
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshots of Invoice 3 ($50.00) vs Invoice 4 ($100.00) + subscription chatter log.
