# Brightloop Subscription Management System — Functional QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Execution (Not Run)
- **Scope:** Normal, Boundary, Negative, and Permission-based verification across all subscription lifecycle areas.
- **Traceability:** Maps directly to `docs/subscription-requirements.md` and `docs/subscription-workflow.md`.

---

## 1. Test Suite Summary

| Category Code | Functional Area | Normal | Boundary | Negative | Permission | Total Test Cases |
|---|---|---|---|---|---|---|
| **TC-REG** | Customer Registration & Profiles | 2 | 1 | 2 | 1 | 6 |
| **TC-ROLE** | Security Roles & Access Control | 1 | 0 | 1 | 3 | 5 |
| **TC-PROD** | Products & Product Variants | 2 | 2 | 2 | 1 | 7 |
| **TC-PLAN** | Subscription Plans & Pricing | 2 | 2 | 2 | 1 | 7 |
| **TC-BILL** | Billing Frequency & Min Quantities | 2 | 3 | 2 | 1 | 8 |
| **TC-QT** | Quotation Templates & Quoting | 2 | 1 | 2 | 1 | 6 |
| **TC-LIFE** | Subscription Lifecycle Transitions | 3 | 2 | 3 | 2 | 10 |
| **TC-OPS** | Pause, Renewal & Closure Operations | 3 | 2 | 2 | 1 | 8 |
| **Total** | | **17** | **13** | **16** | **11** | **57** |

---

## 2. Test Cases

### 2.1 Customer Registration & Portal Profiling (TC-REG)

#### TC-REG-001 (Normal): Successful Portal Customer Registration
- **Traceability:** REQ-SUB-001
- **Test Type:** Normal
- **Preconditions:** Odoo portal signup enabled in system parameters.
- **Test Data:**
  - Name: `Acme Retail Corp`
  - Email: `billing@acmeretail.example.com`
  - Password: `SecurePassword123!`
- **Execution Steps:**
  1. Navigate to `/web/signup` on customer portal.
  2. Input Name, Email, and Password.
  3. Submit registration form.
  4. Verify mailbox for activation email and click confirmation link.
- **Expected Result:** Customer account created in `res.partner`; assigned to `base.group_portal`; `is_subscription_customer` is `True`; user is redirected to portal subscription dashboard.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REG-002 (Negative): Duplicate Email Registration Prevention
- **Traceability:** REQ-SUB-001
- **Test Type:** Negative
- **Preconditions:** Partner record already exists with email `billing@acmeretail.example.com`.
- **Test Data:** Same email `billing@acmeretail.example.com` with different user name.
- **Execution Steps:**
  1. Navigate to `/web/signup`.
  2. Enter identical email with new name.
  3. Click Register.
- **Expected Result:** Registration blocked; validation message displayed: `"Another user is already registered using this email address"`; duplicate record NOT created.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REG-003 (Boundary): Max Length & Special Characters in Customer Metadata
- **Traceability:** REQ-SUB-001, REQ-SUB-002
- **Test Type:** Boundary
- **Preconditions:** Logged in as Subscription Staff.
- **Test Data:**
  - Name: 255-character string containing UTF-8 unicode (`Brightloop 🚀 Café & Co. €100 / Mo`)
  - Email: RFC-compliant long email (`subscription.service-customer.account@sub-domain.enterprise-example.com`)
- **Execution Steps:**
  1. Open backend Subscription > Customers > New.
  2. Input long UTF-8 name and RFC-compliant long email.
  3. Save record.
- **Expected Result:** Record saves without truncation, encoding corruption, or SQL string overflow errors.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REG-004 (Negative): Invalid Email Syntax Rejection
- **Traceability:** REQ-SUB-001, REQ-SUB-002
- **Test Type:** Negative
- **Preconditions:** None.
- **Test Data:** `invalid-email-at-domain.com`, `user@`, `@domain.com`, `user@domain..com`
- **Execution Steps:**
  1. Attempt customer creation with invalid email formatting.
  2. Click Save.
- **Expected Result:** Form validation prevents save; inline warning indicates invalid email syntax.
- **Actual Result:** 
- **Status:** Not Run

#### TC-REG-005 (Permission): Customer Portal User Access Boundary
- **Traceability:** REQ-SUB-001, REQ-SUB-004
- **Test Type:** Permission
- **Preconditions:** User logged in with `base.group_portal`.
- **Test Data:** Direct URL manipulation to backend path `/web#action=brightloop_subscription.action_subscription`.
- **Execution Steps:**
  1. Log in as portal customer.
  2. Attempt to navigate directly to backend admin URL.
- **Expected Result:** Access denied; user redirected to portal landing page (`/my/home`) or HTTP 403 Forbidden page; no internal model data exposed.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.2 Security Roles & Access Control (TC-ROLE)

#### TC-ROLE-001 (Permission): Evaluator Role Read-Only Isolation
- **Traceability:** REQ-SUB-003
- **Test Type:** Permission
- **Preconditions:** User assigned to `brightloop_portal.group_evaluator`.
- **Test Data:** Evaluator user credentials.
- **Execution Steps:**
  1. Log in as Evaluator.
  2. Attempt to create a new quotation.
  3. Attempt to modify existing subscription plan pricing.
  4. Attempt to trigger invoice generation.
- **Expected Result:** "Create", "Edit", and "Action" buttons are hidden; write attempts via API/RPC return `AccessError`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-ROLE-002 (Permission): Staff vs Manager Segregation on Plan Creation
- **Traceability:** REQ-SUB-004
- **Test Type:** Permission
- **Preconditions:** User A assigned to `group_subscription_user` (Staff); User B assigned to `group_subscription_manager` (Manager).
- **Test Data:** Subscription Plan "Enterprise Diamond Tier".
- **Execution Steps:**
  1. User A navigates to Subscription > Configuration > Plans.
  2. User A attempts to click "Create" or edit existing plan.
  3. User B navigates to same menu.
- **Expected Result:** For User A, "Create" button is hidden/inactive; saving raises permission error. For User B, full CRUD is allowed.
- **Actual Result:** 
- **Status:** Not Run

#### TC-ROLE-003 (Negative): Subscription Staff Attempting Direct Deletion of Active Subscriptions
- **Traceability:** REQ-SUB-004
- **Test Type:** Negative / Permission
- **Preconditions:** Active subscription record `SUB/2026/00001` exists. User is Subscription Staff.
- **Test Data:** Record ID of active subscription.
- **Execution Steps:**
  1. Staff opens `SUB/2026/00001`.
  2. Selects Action > Delete.
- **Expected Result:** Delete option is either absent or system displays UserError: `"You cannot delete an active subscription. You must close it first."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.3 Products & Product Variants (TC-PROD)

#### TC-PROD-001 (Normal): Create Subscription Service Product with Variants
- **Traceability:** REQ-SUB-005, REQ-SUB-006
- **Test Type:** Normal
- **Preconditions:** Manager logged in; Attributes `Seat Tier` (Values: Starter [1-5], Pro [6-20]) and `Support Level` (Values: Standard, 24/7) configured.
- **Test Data:**
  - Product Name: `Brightloop Cloud Backup`
  - Recurring Invoice: `True`
  - Extra Prices: Pro (+$50/mo), 24/7 Support (+$100/mo)
- **Execution Steps:**
  1. Open Product Template form.
  2. Check "Can be Subscribed" (`recurring_invoice = True`).
  3. Add attributes `Seat Tier` and `Support Level`.
  4. Save product template.
- **Expected Result:** 4 distinct `product.product` variants generated; recurring invoice flag inherited; price extra correctly computed.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PROD-002 (Negative): Adding Non-Subscription Product to Subscription Plan
- **Traceability:** REQ-SUB-005
- **Test Type:** Negative
- **Preconditions:** Standard consumable product `Hardware USB Dongle` exists with `recurring_invoice = False`.
- **Test Data:** `Hardware USB Dongle`
- **Execution Steps:**
  1. Open Subscription Plan form.
  2. In Default Lines, attempt to select `Hardware USB Dongle`.
- **Expected Result:** Domain filter hides non-subscription products from selection dropdown; manual entry raises ValidationError.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PROD-003 (Boundary): Product Variant with Zero List Price (Free Tier)
- **Traceability:** REQ-SUB-007
- **Test Type:** Boundary
- **Preconditions:** Product template configured as Free Community Tier.
- **Test Data:** Unit Price: `$0.00`
- **Execution Steps:**
  1. Add variant with unit price 0.00 to quotation line.
  2. Validate quote and confirm.
- **Expected Result:** System accepts zero-dollar subscription without division-by-zero or invoice generation failure; zero-value invoice generated marked as Paid/Zero.
- **Actual Result:** 
- **Status:** Not Run

#### TC-PROD-004 (Negative): Negative Product Price Rejection
- **Traceability:** REQ-SUB-007
- **Test Type:** Negative
- **Preconditions:** Subscription line editing enabled.
- **Test Data:** Unit Price: `$-25.00`
- **Execution Steps:**
  1. Input negative unit price on subscription line.
  2. Save record.
- **Expected Result:** Validation error: `"Unit price cannot be negative for subscription lines. Use promotional discount rules instead."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.4 Subscription Plans & Minimum Quantity Scenarios (TC-PLAN & TC-BILL)

#### TC-PLAN-001 (Normal): Multi-Period Plan Creation (Monthly & Annual)
- **Traceability:** REQ-SUB-008
- **Test Type:** Normal
- **Preconditions:** Subscription Manager logged in.
- **Test Data:**
  - Plan A: Interval `1`, Unit `month`
  - Plan B: Interval `1`, Unit `year`
- **Execution Steps:**
  1. Create Plan A with monthly recurrence.
  2. Create Plan B with annual recurrence.
  3. Save both plans.
- **Expected Result:** Plans saved with proper billing interval fields; auto-invoicing cron recognizes cadence.
- **Actual Result:** 
- **Status:** Not Run

#### TC-BILL-001 (Boundary): Minimum Order Quantity (MOQ) Validation
- **Traceability:** REQ-SUB-011
- **Test Type:** Boundary
- **Preconditions:** Enterprise Plan configured with MOQ = 10 seats.
- **Test Data:**
  - Test A: Qty = 9 (below MOQ)
  - Test B: Qty = 10 (exact MOQ)
  - Test C: Qty = 11 (above MOQ)
- **Execution Steps:**
  1. Create quotation for Test A (Qty 9) and click "Send Quotation".
  2. Create quotation for Test B (Qty 10) and click "Send Quotation".
  3. Create quotation for Test C (Qty 11) and click "Send Quotation".
- **Expected Result:** Test A raises ValidationError: `"Quantity (9) is below the minimum required quantity (10) for this plan."` Test B and C succeed.
- **Actual Result:** 
- **Status:** Not Run

#### TC-BILL-002 (Boundary): Leap Year End-of-Month Date Rollover
- **Traceability:** REQ-SUB-012
- **Test Type:** Boundary
- **Preconditions:** Subscription starts on `2028-01-31` (Leap Year) with Monthly billing cadence.
- **Test Data:** Start Date: `2028-01-31`. Next Expected: `2028-02-29`, then `2028-03-31`, then `2028-04-30`.
- **Execution Steps:**
  1. Activate monthly subscription with start date `2028-01-31`.
  2. Trigger recurring invoice cron for cycle 1.
  3. Trigger recurring invoice cron for cycle 2.
- **Expected Result:** Cycle 1 next invoice date is `2028-02-29` (leap year February). Cycle 2 next invoice date is `2028-03-31` (not reverting to 28th).
- **Actual Result:** 
- **Status:** Not Run

#### TC-BILL-003 (Normal): Mid-Cycle Prorated Seat Addition
- **Traceability:** REQ-SUB-013
- **Test Type:** Normal
- **Preconditions:** Monthly subscription active from Nov 1 to Nov 30 (30 days total). Current date: Nov 16 (15 days remaining).
- **Test Data:** Adding 2 seats @ $100/mo each.
- **Execution Steps:**
  1. Add 2 new seats mid-cycle on Nov 16.
  2. Generate intermediate proration invoice.
- **Expected Result:** Proration ratio calculated as $15/30 = 0.5$. Invoiced amount equals $2 \times \$100 \times 0.5 = \$100.00$. Regular monthly invoice next period bills full $200.00$.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.5 Quotation Templates & Quoting (TC-QT)

#### TC-QT-001 (Normal): Quotation Generation from Pre-Configured Template
- **Traceability:** REQ-SUB-014
- **Test Type:** Normal
- **Preconditions:** Template "SaaS Starter Kit" exists with 2 predefined service products, 1-year term, and standard SLA text.
- **Test Data:** Customer `Globex Corp`.
- **Execution Steps:**
  1. Open Subscription Quotations > New.
  2. Select Customer `Globex Corp`.
  3. Select Template `SaaS Starter Kit`.
- **Expected Result:** Order lines automatically populate with products, default quantities, descriptions, and contract terms from the template.
- **Actual Result:** 
- **Status:** Not Run

#### TC-QT-002 (Boundary): Quotation Expiration Boundary Enforcement
- **Traceability:** REQ-SUB-015
- **Test Type:** Boundary
- **Preconditions:** Quotation validity window set to 7 days. Quote created on Oct 24, expiring Oct 31, 23:59:59.
- **Test Data:** Quote acceptance attempt at `2026-10-31 23:58:00` vs `2026-11-01 00:01:00`.
- **Execution Steps:**
  1. Attempt portal customer sign & pay at Oct 31 23:58.
  2. Attempt portal customer sign & pay at Nov 01 00:01.
- **Expected Result:** Oct 31 attempt succeeds and confirms order. Nov 01 attempt is rejected with notification: `"This quotation has expired. Please contact sales for an updated quote."`
- **Actual Result:** 
- **Status:** Not Run

#### TC-QT-003 (Negative): Electronic Signature Submission with Incomplete Data
- **Traceability:** REQ-SUB-016
- **Test Type:** Negative
- **Preconditions:** Quotation in `Quotation` state presented on customer portal.
- **Test Data:** Blank signature pad / missing signatory name.
- **Execution Steps:**
  1. Customer opens quotation portal view.
  2. Clicks "Sign & Pay" without drawing signature or entering full legal name.
- **Expected Result:** Form validation blocks submission; prompts user: `"Please draw your signature and enter your legal name."` State remains `Quotation`.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.6 Subscription Lifecycle Transitions (TC-LIFE)

#### TC-LIFE-001 (Normal): End-to-End Golden Path Lifecycle
- **Traceability:** REQ-SUB-017, REQ-SUB-018, REQ-SUB-019
- **Test Type:** Normal
- **Preconditions:** Standard customer, product, and monthly plan configured.
- **Test Data:** 5 seats @ $50/mo, Prepaid billing.
- **Execution Steps:**
  1. Staff creates Draft subscription (`SUB/DRAFT/00101`).
  2. Staff clicks "Send Quotation" $\rightarrow$ verify state is `Quotation`.
  3. Customer accepts quote via portal $\rightarrow$ verify state is `Confirmed`.
  4. Payment processed $\rightarrow$ verify state is `Active`.
  5. Commitment term finishes $\rightarrow$ verify state transitions to `Closed`.
- **Expected Result:** Every transition succeeds sequentially; timestamps and audit logs populated at each step.
- **Actual Result:** 
- **Status:** Not Run

#### TC-LIFE-002 (Negative): Invalid Direct Jump from Draft to Active
- **Traceability:** REQ-SUB-017, REQ-SUB-019
- **Test Type:** Negative
- **Preconditions:** Subscription in `Draft` state.
- **Test Data:** Draft record `SUB/DRAFT/00102`.
- **Execution Steps:**
  1. Attempt to execute `action_activate()` directly via backend button or RPC call on Draft record.
- **Expected Result:** System blocks transition and raises ValidationError: `"Cannot activate a subscription in Draft status. Must be Quoted and Confirmed first."`
- **Actual Result:** 
- **Status:** Not Run

#### TC-LIFE-003 (Negative): Invalid Direct Jump from Closed to Active
- **Traceability:** REQ-SUB-017
- **Test Type:** Negative
- **Preconditions:** Subscription in `Closed` state (`SUB/2026/00005`).
- **Test Data:** Closed record.
- **Execution Steps:**
  1. Attempt to invoke `action_activate()` or change status to `Active`.
- **Expected Result:** System blocks transition; UserError: `"Closed subscriptions cannot be reopened. Create a new subscription quotation instead."`
- **Actual Result:** 
- **Status:** Not Run

#### TC-LIFE-004 (Boundary): Zero Subscription Lines Confirmation
- **Traceability:** REQ-SUB-018
- **Test Type:** Boundary / Negative
- **Preconditions:** Subscription created with customer selected but zero line items.
- **Test Data:** Subscription with empty line items.
- **Execution Steps:**
  1. Staff clicks "Send Quotation".
- **Expected Result:** Blocked; ValidationError: `"Cannot generate quotation without at least one subscription product line."`
- **Actual Result:** 
- **Status:** Not Run

---

### 2.7 Pause, Renewal & Closure Operations (TC-OPS)

#### TC-OPS-001 (Normal): Pause and Resume Subscription Execution
- **Traceability:** REQ-SUB-020
- **Test Type:** Normal
- **Preconditions:** Active subscription with next invoice scheduled for Dec 1.
- **Test Data:** Pause requested on Nov 10; resumed on Nov 20 (10 days duration).
- **Execution Steps:**
  1. Click "Pause Subscription", specify reason "Customer Extended Vacation".
  2. Verify subscription is marked `is_paused = True`.
  3. Run recurring invoice cron on Nov 15 $\rightarrow$ verify no invoice generated.
  4. Click "Resume Subscription" on Nov 20.
- **Expected Result:** `is_paused` becomes `False`; `next_invoice_date` shifts by 10 days to Dec 11; service entitlement reinstated.
- **Actual Result:** 
- **Status:** Not Run

#### TC-OPS-002 (Boundary): Exceeding Maximum Allowed Pause Window
- **Traceability:** REQ-SUB-020
- **Test Type:** Boundary / Negative
- **Preconditions:** Plan sets `max_pause_days = 30`.
- **Test Data:** Pause requested with duration 31 days or remaining paused beyond 30 days.
- **Execution Steps:**
  1. Input pause duration of 31 days in pause wizard.
  2. Click Confirm.
- **Expected Result:** Validation error thrown: `"The requested pause period exceeds the maximum permitted duration of 30 days for this plan."`
- **Actual Result:** 
- **Status:** Not Run

#### TC-OPS-003 (Normal): Automated Non-Payment Closure via Cron
- **Traceability:** REQ-SUB-023
- **Test Type:** Normal
- **Preconditions:** Active subscription has overdue unpaid invoice with due date Oct 1. Plan grace period is 15 days. Current simulated date: Oct 17.
- **Test Data:** Invoice `INV/2026/00042` marked Unpaid and Past Due.
- **Execution Steps:**
  1. Trigger automated subscription maintenance cron (`ir.cron`).
  2. Inspect subscription status.
- **Expected Result:** Subscription state transitions to `Closed`; close reason recorded as "Automatic Closure: Non-Payment"; cancellation email notification dispatched to customer.
- **Actual Result:** 
- **Status:** Not Run

#### TC-OPS-004 (Permission): Subscription Staff Attempting Early Closure without Reason Code
- **Traceability:** REQ-SUB-022
- **Test Type:** Negative
- **Preconditions:** Active subscription.
- **Test Data:** Close wizard launched without selecting `close_reason_id`.
- **Execution Steps:**
  1. Click "Close Subscription".
  2. Leave closure reason blank and click Submit.
- **Expected Result:** System refuses closure; highlights mandatory `close_reason_id` field.
- **Actual Result:** 
- **Status:** Not Run
