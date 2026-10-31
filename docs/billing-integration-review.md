# Brightloop Subscription Management System — Billing & Reporting Integration Review

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Review Complete / Awaiting Lead Developer Implementation
- **Reviewer:** Billing, Discounts and Dashboard QA & Documentation Specialist
- **Target Baseline Commit:** `5f6cbf3` / Shared Integration Branch `integration`
- **Reviewed Modules:** `custom_addons/brightloop_billing`, `custom_addons/brightloop_discount`, `custom_addons/brightloop_dashboard`, `custom_addons/brightloop_subscription`
- **Scope:** Stage 8 Architecture & Integration Cross-Check (Data contracts, lifecycle separation, duplicate prevention, tax/discount engine integration, dashboard query integrity).

---

## 1. Executive Summary & Architectural Boundaries

A critical requirement of Stage 8 is verifying that **the billing addon (`brightloop_billing`) does NOT duplicate subscription lifecycle logic**.
- **Role of `brightloop_subscription`:** Owns the contract state machine (`Draft` $\rightarrow$ `Quotation` $\rightarrow$ `Confirmed` $\rightarrow$ `Active` $\rightarrow$ `Closed`), line amendments, pause/resume rules, and commitment renewal terms.
- **Role of `brightloop_billing`:** Pure financial accounting coordination — consumes active subscriptions to generate `account.move` invoices, manage payment reconciliations, calculate taxes, and execute dunning retries.
- **Role of `brightloop_discount`:** Autonomous promotional engine providing discount lines and rate reductions to quotations and invoices.
- **Role of `brightloop_dashboard`:** Read-only analytics layer aggregating data from `brightloop_subscription`, `account.move`, and `account.payment`.

---

## 2. Integration Findings & Defect Register

### Finding: INT-BILL-001 (Priority: Critical)
- **Relevant Model / File:** `custom_addons/brightloop_billing/models/account_move.py` (Extension)
- **Requirement:** Subscription-to-Invoice Relational Integrity (REQ-BILL-006, REQ-BILL-014).
- **Observed Implementation:** Addon directory currently contains placeholder skeleton without `subscription_id` foreign key on `account.move`.
- **Potential Defect:** If the lead developer implements invoice-to-subscription linkage via a loose string reference (e.g. invoice `ref = "SUB/001"`) instead of a relational `fields.Many2one('brightloop.subscription', ondelete='restrict')`, index-backed lookups, automated chatter logging, and cascade protections will fail.
- **Suggested Correction:**
  ```python
  class AccountMove(models.Model):
      _inherit = 'account.move'

      subscription_id = fields.Many2one(
          'brightloop.subscription',
          string='Origin Subscription',
          index=True,
          copy=False,
          ondelete='restrict',
          help='Subscription contract from which this recurring invoice was generated.'
      )
      period_start_date = fields.Date(string='Billing Period Start', index=True, copy=False)
      period_end_date = fields.Date(string='Billing Period End', index=True, copy=False)
  ```

---

### Finding: INT-BILL-002 (Priority: Critical)
- **Relevant Model / File:** `custom_addons/brightloop_billing/models/account_move.py`
- **Requirement:** Idempotency & Duplicate Prevention (REQ-BILL-004).
- **Observed Implementation:** No unique SQL constraints or mutex locks currently defined.
- **Potential Defect:** Concurrent execution of automated cron workers or accidental rapid double-clicking by billing clerks will generate multiple identical customer invoices for the same subscription period, leading to double-charging customers on auto-debit gateways.
- **Suggested Correction:** Implement composite SQL constraint on `account.move` and wrap generation in `SELECT FOR UPDATE`:
  ```sql
  CONSTRAINT _unique_subscription_period_invoice 
  UNIQUE (subscription_id, period_start_date, period_end_date, move_type)
  ```

---

### Finding: INT-BILL-003 (Priority: High)
- **Relevant Model / File:** `custom_addons/brightloop_billing/models/subscription_billing.py` vs `brightloop_subscription`
- **Requirement:** Lifecycle Logic Separation (Non-Duplication).
- **Observed Implementation:** Risk of billing engine re-implementing pause, resume, or cancellation state machines.
- **Potential Defect:** If the billing engine directly updates `subscription_id.state = 'closed'` upon non-payment without calling the formal subscription service method `subscription_id.action_close(reason='non_payment')`, subscription audit chatter, notification hooks, and entitlement revocation routines in `brightloop_portal` will be bypassed.
- **Suggested Correction:** The billing addon must strictly call subscription public service APIs:
  ```python
  # CORRECT: Calling subscription domain method
  subscription.action_close(reason_id=non_payment_reason.id)

  # INCORRECT: Direct ORM write bypassing lifecycle hooks
  subscription.write({'state': 'closed'})
  ```

---

### Finding: INT-BILL-004 (Priority: High)
- **Relevant Model / File:** `custom_addons/brightloop_discount/models/discount_rule.py`
- **Requirement:** Discount Usage Limit Atomic Tracking (REQ-DISC-006, REQ-DISC-008).
- **Observed Implementation:** No database models currently implemented.
- **Potential Defect:** If discount cycle counters (`cycles_applied_count`) or global redemption counters (`total_redemptions_count`) increment upon draft invoice generation rather than posted invoice validation, cancelled drafts will permanently consume customer discount allowances.
- **Suggested Correction:** Hook discount counter increments into `account.move.action_post()`:
  ```python
  def action_post(self):
      res = super().action_post()
      for move in self.filtered(lambda m: m.subscription_id and m.move_type == 'out_invoice'):
          move.subscription_id.apply_discount_cycle_increment()
      return res
  ```

---

### Finding: INT-BILL-005 (Priority: Medium)
- **Relevant Model / File:** `custom_addons/brightloop_dashboard/models/dashboard_report.py`
- **Requirement:** Accrual vs Cash Flow KPI Segregation (KPI-02 vs KPI-04).
- **Observed Implementation:** Dashboard addon is currently an empty skeleton.
- **Potential Defect:** Blending `amount_total` from `account.move` with `account.payment` or treating pro-forma draft invoices as recognized revenue will distort financial reporting presented to executive evaluators.
- **Suggested Correction:** Ensure backend SQL queries or RPC controllers distinctly query:
  - Invoiced Revenue $\rightarrow$ `account_move` where `state = 'posted'` and `move_type = 'out_invoice'`.
  - Cash Received $\rightarrow$ `account_payment` where `state = 'posted'` and `payment_type = 'inbound'`.

---

### Finding: INT-BILL-006 (Priority: Medium)
- **Relevant Model / File:** `custom_addons/brightloop_billing/models/account_move.py`
- **Requirement:** Anchor-Preserving End-of-Month Date Arithmetic (REQ-BILL-002).
- **Observed Implementation:** Pending implementation by lead developer.
- **Potential Defect:** Relying on naive standard Odoo date math (`date + relativedelta(months=1)`) will cause permanent billing date drift for subscriptions initiated on the 29th, 30th, or 31st of a month.
- **Suggested Correction:** Store `billing_day_of_month` as an integer on `brightloop.subscription` and use calendar-clamping logic during every billing cycle computation.

---

## 3. Compliance & Non-Execution Disclaimer
> [!IMPORTANT]
> This integration review represents static code analysis and architectural contract verification. Because the documentation and QA specialist operates without an executable Odoo runtime, **no claims of runtime code verification are made**. Runtime validation must be confirmed by the lead developer through automated CI/CD unit tests.
