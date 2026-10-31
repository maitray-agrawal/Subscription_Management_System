# Functional and Non-Functional Requirements
## Brightloop Subscription Management System

### Source of Truth
This document details all business and technical requirements derived directly from the assignment document (`docs/Subscription_Management_System.pdf`).

---

### 1. User Roles & Access Control
- **Administrator**:
  - Full system control.
  - Exclusive authority to invite and configure internal staff members.
  - Setup products, variant pricing, subscription plans, taxes, and discount rules.
  - Full oversight over billing, payments, and financial dashboards.
- **Internal Staff**:
  - Day-to-day operational handling of subscriptions and quotations.
  - View authorized subscription and invoice records.
  - Execute allowed operational actions (pause, resume, renew, close, register payments).
  - Explicitly restricted from administrative configuration (cannot modify plans, create discount rules, or manage staff users).
- **Customer (Portal User)**:
  - Self-service portal access.
  - Registration with unique email and strict password policy.
  - View only own subscriptions, details, and invoice history.
  - Strict ownership-based access control; absolutely no access to administrative functions or other customers' records.

---

### 2. Customer Registration & Authentication
- Self-registration on web portal with email and password.
- **Email Validation**: Enforce global uniqueness across all system users and partners.
- **Password Policy**:
  - Minimum length strictly greater than 8 characters (>= 9 characters).
  - Must contain at least one uppercase letter (`[A-Z]`).
  - Must contain at least one lowercase letter (`[a-z]`).
  - Must contain at least one special character (`[!@#$%^&*(),.?":{}|<>]`).
- **Password Reset**:
  - Secure tokenized reset link sent to registered email via standard Odoo mail mechanisms.

---

### 3. Products & Variants
- Admin adds products with: Name, Type, Sales Price, Cost Price, and Notes.
- Support product variants (e.g., Brand attribute).
- Configurable price extra for attributes (e.g., selecting the "Odoo" brand adds 560 to the base price).

---

### 4. Subscription Plans
- Configurable billing frequency: **Daily**, **Weekly**, **Monthly**, and **Yearly**.
- Minimum required quantity per plan.
- Availability validity dates (`date_start`, `date_end`).
- Auto-closure option: Automatically close subscriptions when expiry date is reached.
- Granular administrative permissions per plan:
  - `allow_early_closure`: Permitted early closure before expiry.
  - `allow_pause`: Permitted temporary pause and resume.
  - `allow_renewal`: Permitted contract renewal.

---

### 5. Quotation Templates & Subscriptions
- **Quotation Templates**:
  - Pre-packaged templates with default plan and product lines.
  - Set validity duration in days.
- **Subscription Records**:
  - Unique subscription sequence number.
  - Customer (`res.partner`), Plan, Start Date, Expiry Date, Payment Terms.
  - Detailed product lines: Product, Quantity, Unit Price, Taxes, Subtotal.
- **Lifecycle State Machine**:
  - Required flow: `Draft` → `Quotation` → `Confirmed` → `Active` → `Closed`.
  - Pause and Resume states/flags.
  - Strict prevention of invalid state transitions.

---

### 6. Billing & Accounting
- Automated recurring invoice generation via scheduled action (`ir.cron`).
- Calculation of exact billing periods and next billing date pointers.
- Reuses native `account.move` (`out_invoice`) and native `account.tax` calculations.
- Invoice actions: Confirm (Post), Cancel, Send, and Print.
- Zero tolerance for duplicate invoicing or skipped billing intervals.
- Billing audit log (`brightloop.billing.log`) recording execution date, periods, invoice ID, status, and error details.
- Native payment registration via `account.payment.register` ensuring proper journal entries and line reconciliation. Direct modification of `payment_state` is strictly forbidden.

---

### 7. Discount Engine
- Admin-only discount creation.
- Discount types: Fixed amount or Percentage.
- Eligibility requirements: Minimum purchase amount, minimum item quantity, active date range.
- Usage limits: Global usage cap tracking (`usage_limit` vs `current_usage_count`).
- Scope: Whole subscription or specific product lines.
- Automatic application: Automatically applied as discount lines on eligible recurring invoices until expired or exhausted.

---

### 8. Financial Dashboard & Performance
- Real-time KPI Cards:
  - Active subscription count.
  - Invoiced revenue vs. Posted revenue vs. Cash received vs. Outstanding receivables.
  - Overdue invoices count and total amount.
  - Subscription status breakdown.
- Date filters (This Month, Last Month, This Quarter, Custom Range).
- Non-functional requirement: High-performance SQL aggregation responding in under 2 seconds even with thousands of subscriptions.
