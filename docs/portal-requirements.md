# Brightloop Subscription Management System — Customer Portal Requirements

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Specification for Lead Developer Implementation
- **Functional Scope:** Customer self-registration, authentication, password policies, password reset, self-service subscription and invoice visibility, payment tracking, and strict record ownership access controls.
- **Relevant Addon:** `brightloop_portal`, `brightloop_base`
- **Author:** Subscription & Customer Portal QA Specialist

---

## 1. Business Context & Problem Statement

Derived directly from the Assignment:
> *"A small business finds Brightloop online and creates an account with their email and a password. Each email can belong to only one account, and the password must be more than eight characters, with an uppercase letter, a lowercase letter and a special character. If they forget it later, a reset link should arrive at their registered email.*
> *Not everyone who logs in should see the same things. The admin controls the whole system, internal staff handle day-to-day work with limited access, and customers see only their own subscriptions and invoices through a portal."*

Today, customers must email staff to check subscription status, ask when renewals are due, or obtain invoice copies. The Customer Portal transforms Brightloop into a self-service platform while strictly safeguarding privacy and commercial security.

---

## 2. Detailed Functional Requirements

### 2.1 Customer Registration & Identity
- **REQ-POR-001 (Portal Self-Signup):**
  - Public visitors must be able to register an account from `/web/signup` or `/brightloop/signup`.
  - Required registration fields: Name, Email address, and Password.
  - Automatically provisions a portal contact in `res.partner` and a user account in `res.users` with `group_brightloop_portal` (`base.group_portal`).
- **REQ-POR-002 (Unique Email Validation):**
  - Every customer email must be globally unique across all active and inactive users and customer partners.
  - Submitting an existing email must be rejected with an informative error message: *"An account with this email address already exists."*
  - Case-insensitive email comparison (e.g., `user@domain.com` matches `USER@domain.com`).
- **REQ-POR-003 (Strict Password Policy):**
  - Passwords must be validated server-side on creation and password reset:
    1. **Length:** Strictly greater than 8 characters ($\ge 9$ characters).
    2. **Uppercase:** Contains at least one uppercase ASCII letter (`[A-Z]`).
    3. **Lowercase:** Contains at least one lowercase ASCII letter (`[a-z]`).
    4. **Special Character:** Contains at least one special character (`[!@#$%^&*(),.?":{}|<>]`).
  - Passwords failing any criterion must be rejected with exact policy feedback.
- **REQ-POR-004 (Secure Password Reset):**
  - If a customer forgets their password, they can request a reset from `/web/reset_password`.
  - System generates a secure, time-limited token and sends a reset link to their verified email address.
  - Reset link leads to password update form enforcing the same strict password policy as registration.

---

### 2.2 Customer Portal Navigation & Views
- **REQ-POR-005 (Portal Home Dashboard):**
  - Logged-in customers at `/my` or `/my/home` must see dedicated tiles for:
    1. **My Subscriptions** (displaying count of active/pending subscriptions).
    2. **My Invoices** (displaying count of invoices and outstanding balance).
- **REQ-POR-006 (Customer Subscription List View):**
  - Accessible via `/my/subscriptions`.
  - Displays table of all subscriptions belonging to the logged-in customer:
    - Subscription Number (e.g., `SUB/2026/00001`).
    - Subscription Plan Name.
    - Start Date.
    - Next Billing Date.
    - Total Amount & Billing Recurrence.
    - Status Badge (`Quotation`, `Confirmed`, `Active`, `Paused`, `Closed`).
- **REQ-POR-007 (Customer Subscription Detail View):**
  - Accessible via `/my/subscriptions/<int:subscription_id>`.
  - Displays full contract details:
    - Plan specifications and recurrence.
    - Line items: Product Name, Variant Details, Quantity, Unit Price, Taxes, Subtotal.
    - Total Recurring Cost and Currency.
    - Payment Terms.
    - History of related invoices.
    - Self-service actions (e.g., Close Early or Pause, *only if permitted by the plan*).
- **REQ-POR-008 (Customer Invoices List & Detail View):**
  - Accessible via `/my/invoices` and `/my/invoices/<int:invoice_id>`.
  - Displays invoice number, invoice date, due date, amount total, and payment status (`Paid`, `Not Paid`, `In Payment`, `Reversed`).
  - Provides downloadable official PDF invoice.
- **REQ-POR-009 (Payment Information Visibility):**
  - Customers can view transaction reference, payment date, payment method/journal, and amount paid against their invoices.
  - Confidential internal payment notes or bank reconciliation journals are hidden from the portal view.

---

### 2.3 Strict Ownership-Based Access Controls
- **REQ-POR-010 (Customer Record Isolation):**
  - A customer must **strictly and exclusively** view their own subscription and invoice records.
  - Record rules (`ir.rule`) must enforce this at the database/ORM level:
    ```python
    ['|', ('partner_id', '=', user.partner_id.id), ('partner_id', 'child_of', user.partner_id.commercial_partner_id.id)]
    ```
- **REQ-POR-011 (Direct URL & ID Manipulation Defense):**
  - If Customer A attempts to access `/my/subscriptions/<ID_OF_CUSTOMER_B>` or `/my/invoices/<ID_OF_CUSTOMER_B>` by guessing or altering the URL parameter:
    - The controller and ORM must return an HTTP 403 (Forbidden) or HTTP 404 (Not Found).
    - Under no circumstances shall Customer A receive Customer B's commercial or billing data.
- **REQ-POR-012 (Administrative Protection):**
  - Portal customers must be blocked from all backend administrative routes (`/web`, `/web/action/*`, `/web/dataset/*`).
  - Attempting to access backend menus redirects customers back to `/my`.
