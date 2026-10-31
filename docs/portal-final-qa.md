# Brightloop Subscription Management System — Customer Portal Acceptance QA Checklist

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Test Ready (Not Run — Execution reserved for Lead Developer)
- **Scope:** Acceptance checklist for customer registration, authentication security, password policies, self-service portals, and cross-customer data isolation.
- **Traceability:** Maps to Assignment Section 3 (*"A new customer signs up"*).
- **Author:** Subscription & Customer Portal QA Specialist

---

## Acceptance Testing Checklist

| Test ID | Scenario Description | Preconditions | Test Data & Steps | Expected Result | Actual Result | Status | Required Evidence |
|---|---|---|---|---|---|---|---|
| **ACC-POR-001** | Customer Self-Registration | Public portal available | 1. Open `/web/signup`.<br>2. Name: `Delta Cloud Ltd`<br>3. Email: `billing@deltacloud.com`<br>4. Password: `DeltaCloud2026!`<br>5. Submit | 1. Account created in `res.users` with portal group.<br>2. User redirected to `/my` portal home. | | Not Run | User record screenshot in portal and backend |
| **ACC-POR-002** | Duplicate Email Rejection | Account with email exists | 1. Attempt signup with identical email `billing@deltacloud.com`. | 1. Registration blocked.<br>2. Error: *"Another user is already registered using this email address"*. | | Not Run | Error notification screenshot |
| **ACC-POR-003** | Password Policy: Length Check | On signup page | 1. Enter password `Pass123!` (8 characters).<br>2. Submit | 1. Submission rejected.<br>2. Error indicates password must be more than 8 characters long. | | Not Run | Password validation message screenshot |
| **ACC-POR-004** | Password Policy: Uppercase Check | On signup page | 1. Enter password `deltacloud2026!` (no uppercase).<br>2. Submit | 1. Submission rejected.<br>2. Error indicates missing uppercase character. | | Not Run | Password validation message screenshot |
| **ACC-POR-005** | Password Policy: Lowercase Check | On signup page | 1. Enter password `DELTACLOUD2026!` (no lowercase).<br>2. Submit | 1. Submission rejected.<br>2. Error indicates missing lowercase character. | | Not Run | Password validation message screenshot |
| **ACC-POR-006** | Password Policy: Special Char Check | On signup page | 1. Enter password `DeltaCloud2026` (no special char).<br>2. Submit | 1. Submission rejected.<br>2. Error indicates missing special character. | | Not Run | Password validation message screenshot |
| **ACC-POR-007** | Secure Password Reset Flow | Registered customer | 1. Open `/web/reset_password`.<br>2. Submit `billing@deltacloud.com`.<br>3. Inspect email reset link with token.<br>4. Set new password `NewSecureDelta2026$`. | 1. Reset link received.<br>2. New password enforces policy.<br>3. Login succeeds with new credentials. | | Not Run | Mail log / screenshot of password reset form |
| **ACC-POR-008** | Customer Views Own Subscriptions | Customer has subscriptions | 1. Log in as `billing@deltacloud.com`.<br>2. Open `/my/subscriptions`. | 1. Table lists all Delta Cloud subscriptions.<br>2. Status badges and totals match backend. | | Not Run | Screenshot of `/my/subscriptions` table |
| **ACC-POR-009** | Customer Views Subscription Detail | Subscription `SUB/0001` exists | 1. Click `SUB/0001` from table. | 1. Shows line items, variant "Brand: Odoo", quantities, unit prices, taxes, and subtotal. | | Not Run | Screenshot of subscription detail view |
| **ACC-POR-010** | Customer Views Invoices & Downloads PDF | Invoice issued to customer | 1. Open `/my/invoices`.<br>2. Click invoice `INV/0001`.<br>3. Click **Download PDF**. | 1. Shows invoice breakdown and payment status.<br>2. Official PDF downloads cleanly. | | Not Run | Downloaded PDF screenshot |
| **ACC-POR-011** | URL Tampering: Cross-Customer Subscription ID | Customer A logged in | 1. Customer A opens `/my/subscriptions/<ID_OF_CUSTOMER_B>`. | 1. HTTP 403 Forbidden or 404 Not Found returned.<br>2. Customer B data NEVER leaked. | | Not Run | HTTP 403 / 404 error page screenshot |
| **ACC-POR-012** | URL Tampering: Cross-Customer Invoice ID | Customer A logged in | 1. Customer A opens `/my/invoices/<ID_OF_CUSTOMER_B>`. | 1. HTTP 403 / 404 returned.<br>2. Zero data leakage. | | Not Run | HTTP 403 / 404 error page screenshot |
| **ACC-POR-013** | Backend Access Blocked for Portal Customer | Customer logged in | 1. In browser, navigate to `/web#action=...`. | 1. Backend interface does not render.<br>2. User redirected to `/my`. | | Not Run | Browser redirect screenshot |
