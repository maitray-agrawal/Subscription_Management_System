# System Architecture
## Brightloop Subscription Management System

### Architecture Overview
The system is architected as a modular suite of six cohesive custom Odoo 19 addons built atop Odoo 19 Enterprise.

```text
custom_addons/
├── brightloop_base/          # Common security groups, roles, and root menus
├── brightloop_subscription/  # Product variants, plans, templates, subscriptions & lifecycle
├── brightloop_billing/       # Recurring invoicing, billing logs, payment integration
├── brightloop_discount/      # Discount rules, usage caps, and auto-invoice application
├── brightloop_portal/        # Customer registration, password policy, portal views
└── brightloop_dashboard/     # High-performance financial KPIs and reports (<2s)
```

### Module Responsibilities & Boundary Separation

1. **`brightloop_base`**:
   - Acts as the foundational anchor for all Brightloop applications.
   - Defines system security groups: `group_brightloop_admin`, `group_brightloop_user`, `group_brightloop_portal`.
   - Defines top-level Brightloop navigation menu hierarchy.
   - Depends only on `base` and `mail`.

2. **`brightloop_subscription`**:
   - Governs the commercial definition of products, variants, plans, and subscriptions.
   - Extends `product.template` and `product.attribute.value` for subscription variant pricing.
   - Defines `brightloop.subscription.plan` supporting daily, weekly, monthly, yearly cycles.
   - Defines `brightloop.quotation.template` and line models.
   - Implements `brightloop.subscription` with strict 5-stage state machine (`Draft` → `Quotation` → `Confirmed` → `Active` → `Closed`) and pause/resume/renew workflows.
   - Depends on `brightloop_base`, `product`.

3. **`brightloop_billing`**:
   - Manages recurring invoice lifecycle without duplicating Odoo accounting models.
   - Creates and posts native `account.move` (`out_invoice`) customer invoices with full tax breakdowns.
   - Implements automated scheduled action (`ir.cron`) and manual invoice triggers.
   - Manages billing schedule and next invoice date calculation.
   - Manages `brightloop.billing.log` for audit trails and idempotency verification.
   - Bridges payment registration using native `account.payment.register` and bank reconciliation.
   - Depends on `brightloop_subscription`, `account`, `account_payment`.

4. **`brightloop_discount`**:
   - Admin-managed discount rules (`brightloop.discount.rule`).
   - Supports fixed amount and percentage discounts with threshold rules (min purchase, min quantity, date range, usage limit).
   - Tracks audit logs via `brightloop.discount.usage`.
   - Automatically injects discount lines during recurring invoice generation.
   - Depends on `brightloop_subscription`, `brightloop_billing`.

5. **`brightloop_portal`**:
   - Extends Odoo's web and portal controllers.
   - Implements customer self-service registration with strict password policy and email uniqueness validation.
   - Provides customer self-service views for active subscriptions and related invoices.
   - Enforces record-level security rules ensuring strict data isolation across customers.
   - Depends on `brightloop_subscription`, `brightloop_billing`, `portal`.

6. **`brightloop_dashboard`**:
   - Financial intelligence and executive reporting interface.
   - Computes real-time KPI metrics (Active Subscriptions, Invoiced Revenue, Posted Revenue, Cash Received, Outstanding Receivables, Overdue Invoices).
   - Employs direct indexed PostgreSQL aggregation queries designed to execute in under 2 seconds.
   - Depends on `brightloop_subscription`, `brightloop_billing`.
