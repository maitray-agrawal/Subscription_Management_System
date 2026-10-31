# Functional and Non-Functional Requirements

## Overview
This document outlines the core functional and non-functional requirements for the Brightloop Subscription Management System across all operational modules.

## Module Specific Requirement Documents

- **Subscription Management (Core Lifecycle, Plans, Quotations, QA):**
  Refer to [`docs/subscription-requirements.md`](./subscription-requirements.md) for the detailed Requirement Traceability Matrix (REQ-SUB-001 through REQ-SUB-023).
- **Subscription Workflow & Lifecycle Specification:**
  Refer to [`docs/subscription-workflow.md`](./subscription-workflow.md) for state transition constraints, pause/renewal scenarios, and role permissions.
- **Subscription Functional QA Test Suite:**
  Refer to [`docs/subscription-test-cases.md`](./subscription-test-cases.md) for comprehensive test cases covering normal, boundary, negative, and permission-based testing.
- **Subscription QA Review Log & Defect Tracking:**
  Refer to [`docs/subscription-review-log.md`](./subscription-review-log.md) for architectural audit findings, edge case analysis, and questions for the lead developer.

---

## High-Level Non-Functional Requirements (NFR)

1. **Security & Data Privacy:**
   - Strict Role-Based Access Control (RBAC) enforced via Odoo Access Control Lists (`ir.model.access.csv`) and Record Rules (`ir.rule`).
   - Customer data isolation ensuring portal users can only access their own subscription contracts and billing documents.
   - Evaluator sandbox accounts must be strictly read-only and prevented from executing commercial transactions.

2. **Auditability & Traceability:**
   - All state transitions, cancellations, pause events, and electronic signatures must be permanently recorded with timestamp, user ID, and IP address in the Odoo chatter/audit trail (`mail.thread`).

3. **Performance & Scalability:**
   - Automated recurring invoicing and subscription maintenance cron jobs must execute in batched chunks to prevent database lock contention or timeout failures on high-volume contract databases.

4. **Reliability & Idempotency:**
   - Cron-based recurring invoice generation must be strictly idempotent to prevent duplicate invoicing for the same billing cycle.
