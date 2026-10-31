# Functional and Non-Functional Requirements

## Overview

This document outlines the core functional and non-functional requirements for the Brightloop Subscription Management System across all operational modules.

---

## Module-Specific Requirement Documents

### Subscription Management

- **Subscription Management (Core Lifecycle, Plans, Quotations, QA):** Refer to `docs/subscription-requirements.md` for the detailed Requirement Traceability Matrix (REQ-SUB-001 through REQ-SUB-023).
- **Subscription Workflow & Lifecycle Specification:** Refer to `docs/subscription-workflow.md` for state transition constraints, pause/renewal scenarios, and role permissions.
- **Subscription Functional QA Test Suite:** Refer to `docs/subscription-test-cases.md` for test cases covering normal, boundary, negative, and permission-based testing.
- **Subscription QA Review Log & Defect Tracking:** Refer to `docs/subscription-review-log.md` for architectural audit findings, edge case analysis, and questions for the lead developer.

### Stage 4: Billing and Accounting

- **Billing & Invoicing Specification:** Refer to `docs/billing-requirements.md`.
- **Billing, Payment & Accounting QA Test Cases:** Refer to `docs/billing-test-cases.md`.
- **Recurring Billing Pipeline & State Machine:** Refer to `docs/recurring-billing-workflow.md`.
- **Dedicated Payment & Accounting Reconciliation Test Suite:** Refer to `docs/payment-test-cases.md`.

### Stage 5: Discount Engine

- **Discount Engine Specification:** Refer to `docs/discount-requirements.md`.
- **Discount Engine QA Test Cases:** Refer to `docs/discount-test-cases.md`.
- **Discount Calculation Worked Examples:** Refer to `docs/discount-calculation-examples.md`.

### Stage 7: Dashboard

- **Dashboard KPI Definitions & Formulas:** Refer to `docs/dashboard-kpi-definitions.md`.
- **Dashboard QA Test Cases:** Refer to `docs/dashboard-test-cases.md`.
- **Performance Criteria & Benchmarking SLAs:** Refer to `docs/dashboard-performance-criteria.md`.

### Stage 8: Integration Review

- **Billing & Reporting Integration Review & Defect Register:** Refer to `docs/billing-integration-review.md`.
- **Pre-Implementation Review Log:** Refer to `docs/billing-review-log.md`.

### Stage 9: Final QA & Evaluator Documentation

- **Billing Final Acceptance QA Protocol:** Refer to `docs/billing-final-qa.md`.
- **Discount Final Acceptance QA Protocol:** Refer to `docs/discount-final-qa.md`.
- **Dashboard Final Acceptance QA Protocol:** Refer to `docs/dashboard-final-qa.md`.
- **Evaluator Demonstration Walkthrough Guide:** Refer to `docs/billing-evaluator-guide.md`.

---

## High-Level Non-Functional Requirements (NFR)

### 1. Security and Data Privacy

- Strict Role-Based Access Control (RBAC) enforced through Odoo Access Control Lists (`ir.model.access.csv`) and Record Rules (`ir.rule`).
- Customer data isolation ensuring portal users can access only their own subscription contracts and billing documents.
- Evaluator sandbox accounts must be read-only and prevented from executing commercial transactions.

### 2. Auditability and Traceability

- All state transitions, cancellations, pause events, and electronic signatures must be recorded with timestamps and user identity in the Odoo chatter/audit trail (`mail.thread`).
- Payment registrations, chargebacks, credit notes, and discount applications must have an appropriate audit trail.

### 3. Performance and Scalability

- Automated recurring invoicing and subscription maintenance cron jobs must execute in batches to reduce database lock contention and timeout failures.
- Financial dashboards should target a load time below 2 seconds on databases containing at least 50,000 subscriptions.
- Appropriate database indexes and optimized queries must support reporting and multi-period aggregations.
- Materialized views may be considered where justified by measured performance requirements.

### 4. Reliability and Idempotency

- Cron-based recurring invoice generation must be idempotent to prevent duplicate invoices for the same subscription and billing period.
- Database-level constraints and appropriate transaction locking must protect against concurrent duplicate billing.

### 5. Accounting Accuracy

- Invoiced revenue must reflect posted customer invoices (`account.move`).
- Cash received must reflect posted and reconciled payment transactions using native Odoo accounting records.
- Unposted draft and pro-forma documents must not be counted as recognized invoiced revenue.
- Tax computation and discount application must preserve accounting accuracy.

### 6. Data Integrity

- Financial and subscription records must maintain consistent relationships.
- Cancellation, retry, renewal, and discount usage operations must not produce duplicate or inconsistent records.
- Access restrictions must be enforced at the server and database-operation level through Odoo's security mechanisms.