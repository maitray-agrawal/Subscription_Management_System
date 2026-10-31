# Functional and Non-Functional Requirements

## Overview
This document outlines the core functional and non-functional requirements for the Brightloop Subscription Management System across all operational modules.

---

## Complete Documentation Index (Stages 4, 5, 7, 8 & 9)

### Stage 4: Billing and Accounting
- **Billing & Invoicing Specification:** [`docs/billing-requirements.md`](./billing-requirements.md)
- **Billing, Payment & Accounting QA Test Cases:** [`docs/billing-test-cases.md`](./billing-test-cases.md)
- **Recurring Billing Pipeline & State Machine:** [`docs/recurring-billing-workflow.md`](./recurring-billing-workflow.md)
- **Dedicated Payment & Accounting Reconciliation Test Suite:** [`docs/payment-test-cases.md`](./payment-test-cases.md)

### Stage 5: Discount Engine
- **Discount Engine Specification:** [`docs/discount-requirements.md`](./discount-requirements.md)
- **Discount Engine QA Test Cases:** [`docs/discount-test-cases.md`](./discount-test-cases.md)
- **Discount Calculation Worked Examples:** [`docs/discount-calculation-examples.md`](./discount-calculation-examples.md)

### Stage 7: Dashboard
- **Dashboard KPI Definitions & Formulas:** [`docs/dashboard-kpi-definitions.md`](./dashboard-kpi-definitions.md)
- **Dashboard QA Test Cases:** [`docs/dashboard-test-cases.md`](./dashboard-test-cases.md)
- **Performance Criteria & Benchmarking SLAs (<2s):** [`docs/dashboard-performance-criteria.md`](./dashboard-performance-criteria.md)

### Stage 8: Integration Review
- **Billing & Reporting Integration Review & Defect Register:** [`docs/billing-integration-review.md`](./billing-integration-review.md)
- **Pre-Implementation Review Log:** [`docs/billing-review-log.md`](./billing-review-log.md)

### Stage 9: Final QA & Evaluator Documentation
- **Billing Final Acceptance QA Protocol:** [`docs/billing-final-qa.md`](./billing-final-qa.md)
- **Discount Final Acceptance QA Protocol:** [`docs/discount-final-qa.md`](./discount-final-qa.md)
- **Dashboard Final Acceptance QA Protocol:** [`docs/dashboard-final-qa.md`](./dashboard-final-qa.md)
- **Evaluator 12-Step Demonstration Walkthrough Guide:** [`docs/billing-evaluator-guide.md`](./billing-evaluator-guide.md)

---

## Core Financial & Operational Non-Functional Requirements (NFR)

1. **Idempotency & Duplicate Billing Prevention:**
   - Database-level unique constraints and row-level locks (`SELECT ... FOR UPDATE`) must guarantee that recurring invoice generation never produces duplicate invoices for the same subscription period.

2. **Accounting Accuracy & Accrual vs. Cash Segregation:**
   - Invoiced Revenue must strictly reflect posted customer invoices (`account.move`).
   - Cash Received must strictly reflect posted payment transactions (`account.payment`).
   - Unposted drafts and pro-forma documents must never be counted as company revenue.

3. **Performance & Query Scalability:**
   - Financial dashboards must load within 2.0 seconds (target < 1.2s) on databases containing $\ge 50,000$ subscriptions.
   - Materialized views and composite indexes must be utilized for multi-period aggregations.

4. **Audit Trail & Immutability:**
   - All payment registrations, chargebacks, credit notes, and discount applications must be permanently logged in Odoo chatter (`mail.thread`) with user identity and timestamp.
