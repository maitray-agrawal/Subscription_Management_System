# Functional and Non-Functional Requirements

## Overview
This document outlines the core functional and non-functional requirements for the Brightloop Subscription Management System across all operational modules.

## Billing, Discount & Dashboard Documentation
- **Billing & Invoicing Specification:**
  Refer to [`docs/billing-requirements.md`](./billing-requirements.md) for recurring billing schedules, duplicate invoice prevention, tax calculation, and dunning retry logic.
- **Billing & Accounting QA Test Cases:**
  Refer to [`docs/billing-test-cases.md`](./billing-test-cases.md) for 38 functional QA test cases covering payment registration, reconciliation, overdue aging, and credit notes.
- **Discount Engine Specification:**
  Refer to [`docs/discount-requirements.md`](./discount-requirements.md) for percentage/fixed discounts, minimum thresholds, start/end dates, cycle limits, and exhaustion rules.
- **Discount Engine QA Test Cases:**
  Refer to [`docs/discount-test-cases.md`](./discount-test-cases.md) for 28 test cases covering usage limits, 100% free trials, and boundary expirations.
- **Dashboard KPI Definitions:**
  Refer to [`docs/dashboard-kpi-definitions.md`](./dashboard-kpi-definitions.md) for precise mathematical formulas, ORM filters, and latency SLAs distinguishing accrual invoiced revenue from actual cash received.
- **Billing QA Review Log:**
  Refer to [`docs/billing-review-log.md`](./billing-review-log.md) for architectural audit findings, duplicate billing risk analysis, and questions for the lead developer.

---

## Core Financial & Operational Non-Functional Requirements (NFR)

1. **Idempotency & Duplicate Billing Prevention:**
   - Database-level unique constraints and row-level locks (`SELECT ... FOR UPDATE`) must guarantee that recurring invoice generation never produces duplicate invoices for the same subscription period.

2. **Accounting Accuracy & Accrual vs. Cash Segregation:**
   - Invoiced Revenue must strictly reflect posted customer invoices (`account.move`).
   - Cash Received must strictly reflect posted payment transactions (`account.payment`).
   - Unposted drafts and pro-forma documents must never be counted as company revenue.

3. **Performance & Query Scalability:**
   - Financial dashboards must load within 1.5 seconds on databases containing $\ge 50,000$ subscriptions.
   - Materialized views and composite indexes must be utilized for multi-period aggregations.

4. **Audit Trail & Immutability:**
   - All payment registrations, chargebacks, credit notes, and discount applications must be permanently logged in Odoo chatter (`mail.thread`) with user identity and timestamp.
