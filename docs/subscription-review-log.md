# Brightloop Subscription Management System — Subscription QA Review Log

## Document Overview
- **Document Version:** 1.0.0
- **QA Contributor:** Technical Documentation & QA Contributor
- **Role Constraint:** Non-runtime environment; analysis conducted via static code audit, architecture compliance checks, and requirement gap analysis.
- **Principle:** No claim of code functionality is made without verified execution in a live Odoo 19 environment.

---

## Review Log Index

| Review ID | Date (UTC/IST) | Target Commit | Scope of Review | Findings Status |
|---|---|---|---|---|
| **REV-20261031-01** | 2026-10-31 | `5f6cbf3` | Initial Repository Architecture & Addon Skeleton Audit | **Action Required by Lead Developer** |

---

## Detailed Review Entries

### Review ID: REV-20261031-01
- **Target Commit:** `5f6cbf3849bf37f95f60b92b470cf701d21c46e1`
- **Commit Message:** `chore: initialize Odoo 19 project structure and documentation`
- **Reviewed Modules:** `custom_addons/brightloop_subscription`, `custom_addons/brightloop_base`
- **Reviewer:** Technical Documentation and QA Contributor

#### 1. Scope & Objective
Evaluate the initial skeleton repository against the core subscription business requirements (Customer Registration, Roles, Product Variants, Plan Configuration, Lifecycle State Machine, Pause/Resume, Renewal, and Closure Scenarios) to establish a baseline defect and gap register for the Lead Developer.

#### 2. Architecture & Static Code Findings

| Finding ID | Severity | Area | Description & Current State | Expected Requirement | Recommendation for Lead Developer |
|---|---|---|---|---|---|
| **FIND-ARCH-001** | **High** | Models | `custom_addons/brightloop_subscription/models/__init__.py` contains only `# Model imports will be added here`. No Python models exist yet. | Core models (`brightloop.subscription`, `brightloop.subscription.line`, `brightloop.subscription.plan`, `brightloop.subscription.template`, `brightloop.subscription.close.reason`) are required. | Implement core models inheriting from `mail.thread` and `mail.activity.mixin` for chatter and audit logging. |
| **FIND-ARCH-002** | **High** | Security | `security/README.md` exists, but no `ir.model.access.csv` or XML security definitions exist. | RBAC separation between `group_subscription_user` (Staff), `group_subscription_manager` (Manager), `group_evaluator` (Evaluator), and Customer. | Create `security/subscription_security.xml` with group categories and `security/ir.model.access.csv` defining granular CRUD rights. |
| **FIND-ARCH-003** | **Medium** | Views | `views/` directory is unpopulated. No form views, list/tree views, search filters, or menu items exist. | Dedicated "Subscriptions" top-level menu and submenus for Subscriptions, Plans, Templates, and Configuration. | Create `views/subscription_views.xml`, `views/subscription_plan_views.xml`, and `views/subscription_menus.xml` and register them in `__manifest__.py`. |
| **FIND-ARCH-004** | **Medium** | Automation / Cron | `data/` directory lacks scheduled actions (`ir.cron`). | Automated daily cron jobs required for: (a) recurring invoice generation, (b) renewal notices, (c) auto-closure upon overdue grace period expiry. | Implement scheduled actions in `data/subscription_cron.xml` with safe batching to handle multi-record timeouts. |
| **FIND-ARCH-005** | **Medium** | Automated Testing | `tests/` directory lacks test classes. | Automated Python test cases needed for lifecycle transitions and boundary conditions. | Provide test suite in `tests/test_subscription_lifecycle.py` subclassing `odoo.tests.common.TransactionCase`. |

---

#### 3. Edge Cases & Risk Identification for Lead Developer

1. **Leap Year and End-of-Month Recurrence Rollovers:**
   - *Risk:* Subscriptions starting on January 31 with monthly recurrence could break or incorrectly jump to March 3 if naive `relativedelta(months=1)` or fixed 30-day additions are used.
   - *Requirement:* Must correctly snap to Feb 28 (or Feb 29 on leap year) and preserve the 31st target for subsequent March billing.
2. **Minimum Order Quantity (MOQ) Validation:**
   - *Risk:* Staff or portal customers might adjust line quantities below plan minimums after template population.
   - *Requirement:* Implement `@api.constrains('quantity')` on `brightloop.subscription.line` to validate against plan/product MOQ thresholds.
3. **Mid-Cycle Proration Rounding Discrepancies:**
   - *Risk:* Prorating daily fractions can produce rounding fractions that diverge from the company currency decimal precision.
   - *Requirement:* Ensure proration calculations use `currency_id.round()` at each step before line aggregation.
4. **State Transition Concurrency & Race Conditions:**
   - *Risk:* Simultaneous webhook payment confirmation and staff manual activation could trigger duplicate initial invoices or double entitlement provisioning.
   - *Requirement:* Use database row-level locking (`SELECT ... FOR UPDATE`) or state verification guards inside `action_activate()`.
5. **Deletion Guard on Active Commercial Contracts:**
   - *Risk:* Accidental deletion of records in `Active` or `Closed` states destroys financial audit history.
   - *Requirement:* Override `unlink()` method in `brightloop.subscription` to raise `UserError` unless record is in `Draft` state.

---

#### 4. Questions & Inquiries for Lead Developer

1. **Odoo Base Inheritance:** Will the subscription model inherit directly from `sale.order` (as in Odoo Enterprise `sale_subscription`), or will Brightloop use a standalone clean model `brightloop.subscription` with distinct relational links to `account.move`?
2. **Payment Provider Integration:** What default payment acquirer / payment provider mock should be targeted for the quotation sign-and-pay portal flow?
3. **Grace Period Default:** What is the agreed company default for `grace_period_days` before automated non-payment closure triggers (e.g., 15 days or 30 days)?

---

#### 5. Compliance Disclaimer
> [!IMPORTANT]
> This review represents static analysis and architectural specification auditing. As the documentation/QA contributor operates without a local Odoo execution environment, **no assertion is made that current code runs or passes Odoo tests**. Full functional verification will occur once the lead developer provides executable modules.
