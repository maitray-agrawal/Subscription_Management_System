# Brightloop Subscription Management System — Discount Engine QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Execution (Not Run)
- **Scope:** Normal, Boundary, Negative, and Permission test cases covering fixed and percentage discounts, eligibility thresholds, usage limits, cycle expiration, and stacking rules.
- **Traceability:** Directly maps to `docs/discount-requirements.md`.

---

## 1. Test Suite Summary

| Category Code | Functional Area | Normal | Boundary | Negative | Permission | Total Test Cases |
|---|---|---|---|---|---|---|
| **TC-DISC-TYPE** | Discount Types (Percentage & Fixed) | 2 | 2 | 2 | 1 | 7 |
| **TC-DISC-THOLD**| Minimum Value & Quantity Thresholds | 2 | 2 | 1 | 0 | 5 |
| **TC-DISC-TIME** | Date Ranges & Exact Billing Date Boundary | 2 | 2 | 1 | 0 | 5 |
| **TC-DISC-LIMIT**| Usage Caps & Recurring Cycle Exhaustion | 3 | 2 | 1 | 1 | 7 |
| **TC-DISC-SCOPE**| Product-Specific vs Subscription-Wide | 2 | 1 | 1 | 0 | 4 |
| **Total** | | **11** | **9** | **7** | **1** | **28** |

---

## 2. Test Cases

### 2.1 Discount Types (Percentage & Fixed) (TC-DISC-TYPE)

#### TC-DISC-001 (Normal): Percentage Discount Application (25% Off)
- **Traceability:** REQ-DISC-001
- **Test Type:** Normal
- **Preconditions:** Active subscription with monthly line: 10 seats @ $50.00 = $500.00 subtotal. Discount rule: `PROMO25` (25% off).
- **Test Data:** Subtotal: $500.00. Discount: 25%.
- **Execution Steps:**
  1. Apply discount code `PROMO25` to subscription quotation.
  2. Generate recurring invoice.
- **Expected Result:**
  - Base Amount: `$500.00`
  - Discount Amount: `-$125.00` ($500.00 \times 0.25)
  - Invoice Subtotal: `$375.00`
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-002 (Normal): Fixed Amount Discount ($100 Off)
- **Traceability:** REQ-DISC-002
- **Test Type:** Normal
- **Preconditions:** Subscription with $400.00 monthly subtotal. Discount rule: `WELCOME100` ($100.00 fixed deduction).
- **Test Data:** Fixed deduction: $100.00.
- **Execution Steps:**
  1. Attach `WELCOME100` to subscription.
  2. Trigger invoice generation.
- **Expected Result:**
  - Net invoice subtotal calculated as `$300.00` ($400.00 - $100.00).
  - Discount line explicitly itemized.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-003 (Boundary): 100% Promotional Discount (Free Period)
- **Traceability:** REQ-DISC-001
- **Test Type:** Boundary
- **Preconditions:** Subscription promotional trial: 100% discount.
- **Test Data:** 100% discount on $200 subscription.
- **Execution Steps:**
  1. Apply 100% discount rule and generate invoice.
- **Expected Result:**
  - Invoice total is `$0.00`.
  - Invoice automatically posts and reconciles to `paid` state without attempting credit card gateway charge.
  - Zero-dollar accounting move generated to satisfy audit trail.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-004 (Boundary): Fixed Discount Exceeding Subtotal (Capping at $0.00)
- **Traceability:** REQ-DISC-002
- **Test Type:** Boundary
- **Preconditions:** Subscription monthly line is $60.00. Customer has fixed discount voucher for $100.00.
- **Test Data:** Subtotal: $60.00, Voucher: $100.00.
- **Execution Steps:**
  1. Apply voucher to subscription line and calculate total.
- **Expected Result:**
  - Net invoice total is capped at `$0.00` (does not become negative `-$40.00`).
  - Remaining $40 voucher balance does not generate cash liability unless explicitly configured as stored credit.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-005 (Negative): Invalid Percentage Value Rejection
- **Traceability:** REQ-DISC-001
- **Test Type:** Negative
- **Preconditions:** Manager configuring discount rule.
- **Test Data:** Percent values: `-15%`, `0%`, `105%`.
- **Execution Steps:**
  1. Attempt to save discount rule with -15% or 105%.
- **Expected Result:** Form validation prevents save; ValidationError: `"Discount percentage must be strictly between 0.01% and 100.00%."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.2 Minimum Value & Quantity Thresholds (TC-DISC-THOLD)

#### TC-DISC-006 (Boundary): Minimum Purchase Value Threshold
- **Traceability:** REQ-DISC-003
- **Test Type:** Boundary
- **Preconditions:** Discount rule `SAVE50` gives $50 off on orders with minimum subtotal of $200.00.
- **Test Data:** Order A: $199.99. Order B: $200.00. Order C: $200.01.
- **Execution Steps:**
  1. Apply `SAVE50` to Order A ($199.99) $\rightarrow$ inspect discount.
  2. Apply `SAVE50` to Order B ($200.00) $\rightarrow$ inspect discount.
  3. Apply `SAVE50` to Order C ($200.01) $\rightarrow$ inspect discount.
- **Expected Result:**
  - Order A: Discount not applied; warning displayed: `"Order subtotal ($199.99) is below the minimum required $200.00 for this discount."`
  - Order B: Discount applied ($50 off, Net = $150.00).
  - Order C: Discount applied ($50 off, Net = $150.01).
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-007 (Boundary): Minimum Seat Quantity Threshold
- **Traceability:** REQ-DISC-004
- **Test Type:** Boundary
- **Preconditions:** Volume discount `VOLUME20` offers 20% off for subscriptions with $\ge 10$ seats.
- **Test Data:** Test 1: 9 seats. Test 2: 10 seats.
- **Execution Steps:**
  1. Set subscription quantity to 9 seats and compute total.
  2. Increase quantity to 10 seats and recompute.
- **Expected Result:**
  - 9 seats: 0% discount applied.
  - 10 seats: 20% discount automatically activates across eligible lines.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.3 Date Ranges & Billing Date Boundaries (TC-DISC-TIME)

#### TC-DISC-008 (Boundary): Discount Expiring Exactly on Billing Date
- **Traceability:** REQ-DISC-005, REQ-DISC-011
- **Test Type:** Boundary
- **Preconditions:** Discount valid from `2026-11-01` to `2026-11-30 23:59:59`.
- **Test Data:**
  - Case A: Invoice generated on `2026-11-30 10:00:00`.
  - Case B: Invoice generated on `2026-12-01 00:01:00`.
- **Execution Steps:**
  1. Run billing for Case A on Nov 30.
  2. Run billing for Case B on Dec 01.
- **Expected Result:**
  - Case A (Nov 30): Discount is applied (within valid window).
  - Case B (Dec 01): Discount is omitted (window has expired).
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-009 (Negative): Attempting to Apply Expired Promo Code
- **Traceability:** REQ-DISC-005
- **Test Type:** Negative
- **Preconditions:** Promotional code `SUMMER2026` expired on `2026-08-31`. Current date: `2026-10-31`.
- **Test Data:** Code: `SUMMER2026`.
- **Execution Steps:**
  1. Input `SUMMER2026` on subscription quotation.
  2. Click "Apply".
- **Expected Result:** Discount rejected; user notification: `"Promotional code 'SUMMER2026' expired on August 31, 2026."` No discount line added.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.4 Usage Limits & Recurring Cycle Exhaustion (TC-DISC-LIMIT)

#### TC-DISC-010 (Normal): Introductory Pricing Exhaustion (First 3 Months Only)
- **Traceability:** REQ-DISC-008
- **Test Type:** Normal / Lifecycle
- **Preconditions:** Subscription created with rule: "50% off for first 3 billing cycles" (`max_cycles = 3`). Standard price: $100/mo.
- **Test Data:** Monthly recurring billing cycles 1 through 4.
- **Execution Steps:**
  1. Generate Cycle 1 invoice $\rightarrow$ inspect price and `cycles_applied_count`.
  2. Generate Cycle 2 invoice $\rightarrow$ inspect price.
  3. Generate Cycle 3 invoice $\rightarrow$ inspect price.
  4. Generate Cycle 4 invoice $\rightarrow$ inspect price.
- **Expected Result:**
  - Cycle 1: Bills `$50.00` (count = 1).
  - Cycle 2: Bills `$50.00` (count = 2).
  - Cycle 3: Bills `$50.00` (count = 3).
  - Cycle 4: Discount is automatically removed/exhausted; invoice bills full `$100.00` standard catalog price.
  - Chatter logs notification: `"Introductory discount has completed its 3-cycle duration."`
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-011 (Boundary): Global Usage Cap Exhaustion
- **Traceability:** REQ-DISC-006
- **Test Type:** Boundary
- **Preconditions:** Promotional campaign `EARLYBIRD` capped at 50 total redemptions. Currently 49 redemptions recorded.
- **Test Data:** Customer A and Customer B both attempt checkout.
- **Execution Steps:**
  1. Customer A confirms subscription using `EARLYBIRD`.
  2. Customer B attempts to apply `EARLYBIRD`.
- **Expected Result:**
  - Customer A successfully redeems 50th slot; `total_redemptions_count` reaches 50; campaign status transitions to "Exhausted".
  - Customer B is blocked with message: `"This promotional campaign has reached its redemption limit."`
- **Actual Result:** 
- **Status:** Not Run

#### TC-DISC-012 (Negative): Exceeding Per-Customer Redemption Cap
- **Traceability:** REQ-DISC-007
- **Test Type:** Negative
- **Preconditions:** Promo code `ONEPERUSER` has `max_per_customer = 1`. Customer `Acme Corp` has already redeemed it once.
- **Test Data:** Partner `Acme Corp`.
- **Execution Steps:**
  1. Customer creates a second subscription quote and inputs `ONEPERUSER`.
- **Expected Result:** Application blocked; error message: `"You have already redeemed this promotion on an existing subscription."`
- **Actual Result:** 
- **Status:** Not Run
