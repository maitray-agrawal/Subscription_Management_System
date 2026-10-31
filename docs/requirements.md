# Brightloop Subscription Management System

## Source of Truth

This document consolidates the functional and non-functional requirements derived from the original assignment document (`docs/Subscription_Management_System.pdf`) and the supporting module specifications and QA documentation.

---

## 1. User Roles & Access Control

- **Administrator**
  - Full system control.
  - Exclusive authority to invite and configure internal staff members.
  - Configure products, variant pricing, subscription plans, taxes, and discount rules.
  - Full oversight of billing, payments, and financial dashboards.
- **Internal Staff**
  - Handle day-to-day subscriptions and quotations.
  - View authorized subscription and invoice records.
  - Execute permitted operational actions, including pause, resume, renew, close, and register payments.
  - Cannot modify administrative configuration, create discount rules, or manage staff users.
- **Customer (Portal User)**
  - Access the self-service portal.
  - Register using a unique email and the required password policy.
  - View only their own subscriptions, details, and invoice history.
  - Must not access administrative functions or other customers' records.

---

## 2. Customer Registration & Authentication

- Self-registration through the web portal using email and password.
- **Email validation:** Enforce global uniqueness across system users and partners.
- **Password policy:**
  - Minimum length of 9 characters.
  - At least one uppercase letter (`[A-Z]`).
  - At least one lowercase letter (`[a-z]`).
  - At least one special character (`[!@#$%^&*(),.?":{}|<>]`).
- **Password reset:** Secure tokenized reset link sent to the registered email using standard Odoo mail mechanisms.

---

## 3. Products & Variants

- Administrators can add products with name, type, sales price, cost price, and notes.
- Support product variants, such as a Brand attribute.
- Support configurable price extras for attributes. For example, selecting the "Odoo" brand adds 560 to the base price.

---

## 4. Subscription Plans

- Configurable billing frequency: daily, weekly, monthly, and yearly.
- Minimum required quantity per plan.
- Availability validity dates (`date_start`, `date_end`).
- Auto-closure option to close subscriptions when the expiry date is reached.
- Configurable permissions:
  - `allow_early_closure`: permits early closure before expiry.
  - `allow_pause`: permits temporary pause and resume.
  - `allow_renewal`: permits contract renewal.

---

## 5. Quotation Templates & Subscriptions

### Quotation Templates

- Preconfigured templates with default plan and product lines.
- Configurable validity duration in days.

### Subscription Records

- Unique subscription sequence number.
- Customer (`res.partner`), plan, start date, expiry date, and payment terms.
- Product lines containing product, quantity, unit price, taxes, and subtotal.

### Lifecycle State Machine

Required flow:

`Draft` → `Quotation` → `Confirmed` → `Active` → `Closed`

- Support pause and resume states or flags.
- Prevent invalid state transitions.

---

## 6. Billing & Accounting

- Automated recurring invoice generation through a scheduled action (`ir.cron`).
- Accurate billing-period calculation and next-billing-date tracking.
- Reuse native `account.move` (`out_invoice`) and native `account.tax` calculations.
- Invoice actions: Confirm (Post), Cancel, Send, and Print.
- Prevent duplicate invoicing and skipped billing intervals.
- Maintain a billing audit log (`brightloop.billing.log`) recording execution date, periods, invoice ID, status, and error details.
- Use native payment registration through `account.payment.register`, ensuring proper journal entries and reconciliation.
- Direct modification of `payment_state` is prohibited.

---

## 7. Discount Engine

- Discount creation restricted to administrators.
- Discount types: fixed amount and percentage.
- Eligibility requirements:
  - Minimum purchase amount.
  - Minimum item quantity.
  - Active date range.
- Usage limits through `usage_limit` and `current_usage_count`.
- Scope: entire subscription or specific product lines.
- Automatically apply eligible discounts to recurring invoices until expiry or exhaustion.

---

## 8. Financial Dashboard & Performance

### Dashboard KPIs

- Active subscription count.
- Invoiced revenue.
- Posted revenue.
- Cash received.
- Outstanding receivables.
- Overdue invoice count and total amount.
- Subscription status breakdown.

### Filters

- This Month.
- Last Month.
- This Quarter.
- Custom Date Range.

### Performance Requirement

Financial dashboard queries must respond in under 2 seconds, including when the database contains thousands of subscriptions.

---

## 9. Complete Documentation Index

### Stage 4: Billing and Accounting

- Billing and invoicing specification: `docs/billing-requirements.md`
- Billing, payment, and accounting QA test cases: `docs/billing-test-c