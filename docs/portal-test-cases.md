# Brightloop Subscription Management System — Customer Portal QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Lead Developer Implementation
- **Functional Scope:** Registration validation, password policy compliance, password reset, self-service portals, and negative/security tests (ID manipulation, cross-customer data leakage).
- **Traceability:** Maps to `docs/portal-requirements.md` and `docs/customer-access-matrix.md`.
- **Author:** Subscription & Customer Portal QA Specialist

---

## 1. Test Suite Summary

| Category Code | Focus Area | Normal | Boundary | Negative | Security | Total |
|---|---|---|---|---|---|---|
| **TC-PORT-REG** | Customer Registration & Email Uniqueness | 1 | 1 | 2 | 1 | 5 |
| **TC-PORT-PWD** | Password Policy Enforcement & Reset | 1 | 2 | 4 | 1 | 8 |
| **TC-PORT-VIEW** | Portal Subscription & Invoice Views | 3 | 1 | 1 | 1 | 6 |
| **TC-PORT-SEC** | Customer Data Isolation & URL Tampering | 0 | 0 | 0 | 6 | 6 |
| **Total** | | **5** | **4** | **7** | **9** | **25** |

---

## 2. Test Cases

### 2.1 Customer Registration & Email Uniqueness (TC-PORT-REG)

#### TC-PORT-REG-001 (Normal): Successful Portal Registration
- **Objective:** Verify public visitor can successfully register a new account.
- **Test Data:** Name: `Acme Retailers`, Email: `contact@acmeretailers.com`, Password: `Brightloop2026!`.
- **Execution Steps:**
  1. Navigate to `/web/signup`.
  2. Input valid Name, Email, and compliant Password.
  3. Click **Sign up**.
- **Expected Result:** User is registered, redirected to `/my`, partner record created with `is_subscription_customer = True`, assigned group `group_brightloop_portal`.
- **Status:** Not Run

#### TC-PORT-REG-002 (Negative): Duplicate Email Registration Rejection
- **Objective:** Verify system prevents registering with an email that already exists.
- **Preconditions:** Account exists with email `contact@acmeretailers.com`.
- **Test Data:** Name: `Imposter Corp`, Email: `contact@acmeretailers.com`, Password: `ValidPass123$`.
- **Execution Steps:**
  1. Navigate to `/web/signup`.
  2. Enter duplicate email with new name.
  3. Click **Sign up**.
- **Expected Result:** Form blocks submission; clear error message: *"Another user is already registered using this email address"*; database contains exactly 1 user for this email.
- **Status:** Not Run

#### TC-PORT-REG-003 (Negative): Case-Insensitive Duplicate Email Rejection
- **Objective:** Verify email uniqueness check is case-insensitive.
- **Preconditions:** Account exists with email `contact@acmeretailers.com`.
- **Test Data:** Email: `CONTACT@ACMERETAILERS.COM`.
- **Execution Steps:**
  1. Attempt to register using uppercase version of existing email.
- **Expected Result:** Registration rejected with duplicate email warning.
- **Status:** Not Run

---

### 2.2 Password Policy Enforcement (TC-PORT-PWD)

Policy Requirements:
$$\text{Length} \ge 9 \text{ chars} \quad \land \quad \ge 1 \text{ Uppercase [A-Z]} \quad \land \quad \ge 1 \text{ Lowercase [a-z]} \quad \land \quad \ge 1 \text{ Special Char [!@#\$%^&*(),.?\":{}|<>]}$$

#### TC-PORT-PWD-001 (Negative): Password Too Short ($\le 8$ Characters)
- **Objective:** Enforce rule *"password must be more than eight characters"*.
- **Test Data:** `Abc!1234` (exactly 8 characters).
- **Execution Steps:**
  1. Submit registration with password `Abc!1234`.
- **Expected Result:** Submission rejected; error indicates password must be more than 8 characters long.
- **Status:** Not Run

#### TC-PORT-PWD-002 (Negative): Password Missing Uppercase Letter
- **Objective:** Enforce requirement for uppercase letter.
- **Test Data:** `brightloop2026!` (15 characters, lowercase + number + special char, NO uppercase).
- **Execution Steps:**
  1. Submit registration with password `brightloop2026!`.
- **Expected Result:** Submission rejected; error indicates password must contain at least one uppercase letter.
- **Status:** Not Run

#### TC-PORT-PWD-003 (Negative): Password Missing Lowercase Letter
- **Objective:** Enforce requirement for lowercase letter.
- **Test Data:** `BRIGHTLOOP2026!` (15 characters, uppercase + number + special char, NO lowercase).
- **Execution Steps:**
  1. Submit registration with password `BRIGHTLOOP2026!`.
- **Expected Result:** Submission rejected; error indicates password must contain at least one lowercase letter.
- **Status:** Not Run

#### TC-PORT-PWD-004 (Negative): Password Missing Special Character
- **Objective:** Enforce requirement for special character.
- **Test Data:** `Brightloop2026` (14 characters, uppercase + lowercase + number, NO special char).
- **Execution Steps:**
  1. Submit registration with password `Brightloop2026`.
- **Expected Result:** Submission rejected; error indicates password must contain at least one special character.
- **Status:** Not Run

#### TC-PORT-PWD-005 (Boundary): Password Exactly 9 Characters (Minimum Valid)
- **Objective:** Verify boundary edge case of length = 9 with all required character classes.
- **Test Data:** `Pass1234!` (Length = 9: 1 uppercase, 3 lowercase, 4 digits, 1 special).
- **Execution Steps:**
  1. Submit registration with password `Pass1234!`.
- **Expected Result:** Password accepted; registration succeeds.
- **Status:** Not Run

#### TC-PORT-PWD-006 (Normal): Password Reset Token Flow
- **Objective:** Verify password reset link delivers to registered email and enforces password policy.
- **Preconditions:** Registered user `contact@acmeretailers.com`.
- **Execution Steps:**
  1. Open `/web/reset_password`.
  2. Enter `contact@acmeretailers.com` and submit.
  3. Verify reset email received in mailbox with valid secure token.
  4. Follow reset link.
  5. Attempt reset with non-compliant password `weak` (must fail).
  6. Submit compliant password `NewSecurePassword2026!`.
  7. Log in with new credentials.
- **Expected Result:** Password reset completed successfully; old password no longer authenticates.
- **Status:** Not Run

---

### 2.3 Customer Portal Views & Details (TC-PORT-VIEW)

#### TC-PORT-VIEW-001 (Normal): Customer Views Own Subscriptions List
- **Preconditions:** Customer `Acme Retailers` has 2 active subscriptions and 1 closed subscription.
- **Execution Steps:**
  1. Log into portal as `contact@acmeretailers.com`.
  2. Navigate to `/my/subscriptions`.
- **Expected Result:**
  1. Table displays exactly the 3 subscriptions belonging to Acme Retailers.
  2. Columns include Subscription Number, Plan, Start Date, Next Billing Date, Total, and Status Badge.
  3. No subscriptions of other companies appear.
- **Status:** Not Run

#### TC-PORT-VIEW-002 (Normal): Customer Views Subscription Details
- **Preconditions:** Subscription `SUB/2026/00001` belongs to Acme Retailers.
- **Execution Steps:**
  1. From `/my/subscriptions`, click `SUB/2026/00001`.
- **Expected Result:**
  1. Detail page displays plan name, billing interval, start and expiry dates.
  2. Subscription lines show product name, variant ("Brand: Odoo"), quantity, price, taxes, and subtotal.
  3. Related invoice history is listed with payment status.
- **Status:** Not Run

#### TC-PORT-VIEW-003 (Normal): Customer Views Invoices & Downloads PDF
- **Preconditions:** Invoice `INV/2026/0001` issued to Acme Retailers.
- **Execution Steps:**
  1. Navigate to `/my/invoices`.
  2. View invoice list and click `INV/2026/0001`.
  3. Click **Download PDF**.
- **Expected Result:** Invoice detail shows amounts, tax breakdown, payment date, and status `Paid`. Official PDF downloads cleanly.
- **Status:** Not Run

---

### 2.4 Strict Data Isolation & Cross-Customer Security (TC-PORT-SEC)

#### TC-PORT-SEC-001 (Security): Direct URL Subscription ID Tampering (Horizontal Privilege Escalation)
- **Objective:** Verify Customer A cannot view Customer B's subscription by tampering with URL IDs.
- **Preconditions:**
  - Customer A (`Acme Retailers`, partner ID: 101) owns Subscription ID: `1`.
  - Customer B (`Global Logistics`, partner ID: 102) owns Subscription ID: `2`.
- **Execution Steps:**
  1. Log into portal as Customer A (`contact@acmeretailers.com`).
  2. Verify access to own subscription: `/my/subscriptions/1` (HTTP 200).
  3. In browser address bar, manually change URL to `/my/subscriptions/2` (Customer B's record).
  4. Press Enter.
- **Expected Result:**
  - Request is blocked with **HTTP 403 Forbidden** or **HTTP 404 Not Found**.
  - Customer A NEVER sees Customer B's product lines, prices, or contact details.
- **Status:** Not Run

#### TC-PORT-SEC-002 (Security): Direct URL Invoice ID Tampering
- **Objective:** Verify Customer A cannot view or download Customer B's invoices.
- **Preconditions:**
  - Customer A owns Invoice ID: `10`.
  - Customer B owns Invoice ID: `20`.
- **Execution Steps:**
  1. Log in as Customer A.
  2. Navigate directly to `/my/invoices/20` and `/my/invoices/20/download`.
- **Expected Result:** Access denied (HTTP 403 / 404); download blocked; zero data leakage.
- **Status:** Not Run

#### TC-PORT-SEC-003 (Security): Unauthenticated Portal Access
- **Objective:** Verify unauthenticated public visitors cannot access `/my/*` routes.
- **Execution Steps:**
  1. Open incognito window (no active session).
  2. Navigate directly to `/my/subscriptions`.
- **Expected Result:** System immediately redirects to `/web/login?redirect=/my/subscriptions`.
- **Status:** Not Run

#### TC-PORT-SEC-004 (Security): Portal Customer Blocked from Backend Administration
- **Objective:** Verify portal customers cannot access backend administrative views.
- **Preconditions:** Logged in as Customer A (`group_brightloop_portal`).
- **Execution Steps:**
  1. Attempt to browse to `/web` backend menu, `/web#action=brightloop_base.action_brightloop_config_settings`, or call ORM dataset `/web/dataset/call_kw`.
- **Expected Result:**
  - Backend administrative interface does not load.
  - User is redirected back to `/my` portal home.
  - JSON-RPC requests return access denied.
- **Status:** Not Run

#### TC-PORT-SEC-005 (Security): Portal Customer Cannot View Confidential Accounting Journals
- **Objective:** Verify internal payment memos or bank journal configurations are never exposed on portal invoices.
- **Execution Steps:**
  1. Staff registers payment on Customer A's invoice with internal note: *"Customer disputed late fee, approved waived balance."*
  2. Customer A views `/my/invoices/<id>`.
- **Expected Result:** Customer sees payment date, amount, and payment status, but internal staff note remains strictly hidden.
- **Status:** Not Run

#### TC-PORT-SEC-006 (Security): Database-Level Record Rule Validation via ORM
- **Objective:** Verify that even if a controller code vulnerability occurred, Odoo's SQL record rule intercepts illegal queries.
- **Execution Steps:**
  - Execute ORM search with Customer A's user environment:
    ```python
    self.env['brightloop.subscription'].with_user(customer_a).search([])
    ```
- **Expected Result:** Search domain automatically injects `['|', ('partner_id', '=', partner_a), ('partner_id', 'child_of', commercial_partner_a)]`. Returned recordset contains ONLY Customer A's subscriptions.
- **Status:** Not Run
