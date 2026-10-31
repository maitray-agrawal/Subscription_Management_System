# Brightloop Subscription Management System — Billing, Discount & Dashboard QA Review Log

## Document Overview
- **Document Version:** 1.0.0
- **QA Contributor:** Technical Documentation, Requirements-Analysis & QA Contributor
- **Role Constraint:** Non-runtime environment; analysis conducted via static code auditing, architectural gap analysis, and requirement cross-referencing.
- **Principle:** No claim of code functionality or accounting correctness is made without verified runtime execution in a configured Odoo 19 environment.

---

## Review Log Index

| Review ID | Date (UTC/IST) | Target Commit | Scope of Review | Findings Status |
|---|---|---|---|---|
| **REV-BILL-20261031-01** | 2026-10-31 | `5f6cbf3` | Baseline Audit of `brightloop_billing`, `brightloop_discount`, and `brightloop_dashboard` | **Action Required by Lead Developer** |

---

## Detailed Review Entries

### Review ID: REV-BILL-20261031-01
- **Target Commit:** `5f6cbf3849bf37f95f60b92b470cf701d21c46e1`
- **Commit Message:** `chore: initialize Odoo 19 project structure and documentation`
- **Reviewed Modules:** `custom_addons/brightloop_billing`, `custom_addons/brightloop_discount`, `custom_addons/brightloop_dashboard`
- **Reviewer:** Technical Documentation and QA Contributor

---

### 1. Scope & Objective
Perform a comprehensive pre-implementation code audit of the billing, discount, and dashboard addons to identify architectural vulnerabilities, duplicate billing risks, accounting edge cases, and dashboard query bottlenecks prior to code development.

---

### 2. Implementation Findings & Risk Register

#### A. Missing Functionality & Skeleton State
- **Finding ID:** `FIND-BILL-001` (Severity: High)
- **Area:** Core Models & Automation
- **Current State:** `models/__init__.py` across all three modules contains only placeholder comment `# Model imports will be added here`.
- **Expected Requirement:**
  1. `brightloop_billing`: Needs model extensions on `account.move` and `account.payment` to store `subscription_id`, `period_start_date`, and `period_end_date`. Also requires daily cron `ir.cron_generate_subscription_invoices`.
  2. `brightloop_discount`: Needs discount rule model `brightloop.discount.rule` with fields for fixed/percent types, start/end dates, global and per-customer usage counters, and cycle limits.
  3. `brightloop_dashboard`: Needs reporting view model or controller endpoints delivering aggregated JSON metrics for active subscriptions, invoiced revenue, cash received, and overdue receivables.

#### B. Duplicate Billing Risks (High Risk)
- **Finding ID:** `FIND-BILL-002` (Severity: Critical)
- **Area:** Concurrency & Recurring Cron
- **Risk Analysis:**
  - If the recurring billing cron encounters a slow query or timeout and re-runs, or if a staff member clicks "Generate Invoice" in the UI while the background cron is executing, multiple duplicate customer invoices will be created for the same customer and billing cycle.
- **Recommendation for Lead Developer:**
  - Implement a database SQL unique constraint on `account.move`:
    ```sql
    CONSTRAINT unique_subscription_period_invoice 
    UNIQUE (subscription_id, period_start_date, period_end_date, move_type)
    ```
  - In the Python generation method, wrap the query with `SELECT ... FOR UPDATE SKIP LOCKED` on the subscription record to prevent concurrent worker processes from processing the same subscription.

#### C. Potential Calculation & Calendar Rollover Errors
- **Finding ID:** `FIND-BILL-003` (Severity: Medium)
- **Area:** Next Billing Date Arithmetic
- **Risk Analysis:**
  - Using naive calendar date math (`date + relativedelta(months=1)`) without preserving the original anchor day causes date degradation. For example, a subscription starting on Jan 31 rolling to Feb 28 will permanently remain on the 28th for March, April, etc., rather than snapping back to the 31st.
- **Recommendation for Lead Developer:**
  - Maintain an immutable integer field `billing_day_of_month` (e.g. 31) on `brightloop.subscription`.
  - Calculate `next_invoice_date` using:
    ```python
    target_month = current_date + relativedelta(months=interval)
    max_days = calendar.monthrange(target_month.year, target_month.month)[1]
    next_date = target_month.replace(day=min(subscription.billing_day_of_month, max_days))
    ```

#### D. Accounting Inconsistencies (Accrual vs Cash)
- **Finding ID:** `FIND-BILL-004` (Severity: High)
- **Area:** Payment Reconciliation & Cash Recognition
- **Risk Analysis:**
  - In Odoo, an invoice in `in_payment` state indicates a payment transaction has been created (e.g. pending bank batch or gateway settlement), but has not yet fully reconciled against a bank statement line. Treating `in_payment` as realized cash or double-counting unposted journal entries will distort financial dashboards.
- **Recommendation for Lead Developer:**
  - Strictly filter cash received KPIs on posted `account.payment` records linked to reconciled lines (`account.partial.reconcile`).
  - Keep Invoiced Revenue strictly anchored to posted `account.move` (`state = 'posted'`).

#### E. Discount Boundary & Expiration Handling
- **Finding ID:** `FIND-BILL-005` (Severity: Medium)
- **Area:** Cycle Limits & Exhaustion
- **Risk Analysis:**
  - Discounts limited to $N$ cycles (e.g. "first 3 months") require an atomic counter. If an invoice is generated in Draft and later cancelled, does the counter decrement?
- **Recommendation for Lead Developer:**
  - Increment the `cycles_applied_count` ONLY when the invoice moves from `draft` to `posted`. If a draft invoice is cancelled, the counter remains unaffected.

#### F. Dashboard Performance & Query Latency Risks
- **Finding ID:** `FIND-BILL-006` (Severity: Medium)
- **Area:** Aggregation Query Scalability
- **Risk Analysis:**
  - Calculating total revenue and overdue receivables on-the-fly via unindexed ORM `search()` or Python loops across tens of thousands of `account.move` records will cause unacceptable dashboard loading latency ($>10$ seconds) and worker thread exhaustion.
- **Recommendation for Lead Developer:**
  - Add composite PostgreSQL indexes on `account_move`:
    - `CREATE INDEX idx_move_sub_state ON account_move(subscription_id, state, invoice_date);`
    - `CREATE INDEX idx_move_overdue ON account_move(state, payment_state, invoice_date_due);`
  - Leverage Odoo SQL View models (`_auto = False`) for dashboard data sources.

---

### 3. Open Questions for Lead Developer

1. **Auto-Post vs Manual Review:** Will recurring subscription invoices be created directly in `posted` state and automatically charged, or created in `draft` for a configurable review window prior to auto-posting?
2. **Payment Gateway Integration:** Which specific payment acquirer module (`payment_stripe`, `payment_authorize`, or custom test provider) will handle automated tokenized recurring charges?
3. **Discount Line Presentation:** Should subscription-wide discounts appear as a separate invoice line item mapped to a specific promotional expense account, or as a percentage reduction directly on each subscription product line?
4. **Foreign Currency Handling:** When aggregating multi-currency dashboard KPIs, should amounts convert using the transaction date rate or current rate? (Recommendation: Transaction date rate via `company_currency_id`).

---

### 4. Compliance Disclaimer
> [!IMPORTANT]
> This review represents static analysis and architectural specification auditing. As the documentation/QA contributor operates without a local Odoo execution environment, **no assertion is made that current code runs or passes Odoo tests**. Full functional verification will occur once the lead developer provides executable modules.
