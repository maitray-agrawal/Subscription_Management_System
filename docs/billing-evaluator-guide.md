# Brightloop Subscription Management System — Billing, Discount & Dashboard Evaluator Guide

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Approved
- **Audience:** System Evaluators, Reviewers, and Demonstrators
- **Scope:** Interactive end-to-end demonstration script covering the 12 key billing, discount, and financial dashboard workflows in Odoo 19.

---

## 1. Evaluator Prerequisites & Demonstration Setup

| Parameter | Required Value | Notes |
|---|---|---|
| **ERP Version** | Odoo 19.0 (Community or Enterprise) | Custom addons installed |
| **Installed Addons** | `brightloop_base`, `brightloop_subscription`, `brightloop_billing`, `brightloop_discount`, `brightloop_dashboard` | All modules active |
| **Demo User** | `demo_evaluator` / `Evaluator123!` | Group: Subscription Staff / Evaluator |
| **Demo Partner** | `Acme Global Enterprises` | Pre-configured with USD currency and Standard VAT |
| **Demo Products** | `Brightloop Cloud Pro` ($100/mo), `24/7 Premium Support` ($200/mo) | Recurring subscription products |

---

## 2. Step-by-Step Evaluator Demonstration Workflows

### Workflow 1: Creating a Subscription
1. Navigate to **Subscriptions > Subscriptions > New**.
2. Set **Customer** to `Acme Global Enterprises`.
3. Set **Plan** to `Monthly Business Tier` (Interval: 1 Month).
4. In the **Order Lines** tab, click "Add a line":
   - Product: `Brightloop Cloud Pro`
   - Quantity: `5`
   - Unit Price: `$100.00`
5. Click **Confirm** (or **Send Quotation** $\rightarrow$ **Confirm**).
- **Visual Confirmation Checkpoint:**
  - Status bar updates to **Confirmed** or **Active**.
  - A unique subscription reference is generated (e.g., `SUB/2026/00001`).
  - `next_invoice_date` is populated with today's date.

---

### Workflow 2: Generating its Recurring Invoice
1. On the active subscription form, click the **Generate Invoice** button (or wait for the daily cron).
2. A smart button labeled **Invoices (1)** appears on the upper right. Click it.
3. Open the newly generated invoice (`INV/2026/00001`).
- **Visual Confirmation Checkpoint:**
  - Invoice lines match the subscription lines ($5 \times \$100.00 = \$500.00$).
  - Description states: `"Brightloop Cloud Pro - Coverage: [Start Date] to [End Date]"`.
  - Subscription form view updates `next_invoice_date` to next month.

---

### Workflow 3: Checking Tax Calculation
1. On the open invoice `INV/2026/00001`, inspect the lower-right totals section.
2. Verify:
   - **Untaxed Amount:** `$500.00`
   - **Taxes (Standard 10%):** `$50.00`
   - **Total Amount:** `$550.00`
- **Visual Confirmation Checkpoint:**
  - Tax calculation is explicit; lines display tax rate badges; mathematical formula equals $\text{Untaxed} + \text{Tax}$.

---

### Workflow 4: Applying a Fixed Discount
1. Return to **Subscriptions > New**.
2. Select Customer `Acme Global Enterprises` and add `Brightloop Cloud Pro` (Qty 5 = $500.00).
3. In the **Discounts / Vouchers** section, enter code `FLAT50` ($50.00 Fixed Discount).
4. Click **Apply**.
- **Visual Confirmation Checkpoint:**
  - A discount adjustment line is inserted for `-$50.00`.
  - Untaxed subtotal updates from `$500.00` to `$450.00`.

---

### Workflow 5: Applying a Percentage Discount
1. In order lines, select the discount code `SAVE20` (20% Off).
2. Click **Apply**.
- **Visual Confirmation Checkpoint:**
  - Base subtotal of $500.00 receives 20% reduction ($100.00 off).
  - Invoiced subtotal displays `$400.00`.

---

### Workflow 6: Testing an Expired Discount
1. Attempt to enter promotional voucher `EXPIRED2025` (End Date was `2025-12-31`).
2. Click **Apply**.
- **Visual Confirmation Checkpoint:**
  - An inline warning notification appears: `"Promotional code 'EXPIRED2025' expired on December 31, 2025."`
  - Zero discount is applied to the order lines.

---

### Workflow 7: Testing a Discount Usage Limit
1. Create a promo code `EXCLUSIVE1` configured with `max_global_redemptions = 1`.
2. Customer A applies code and confirms order $\rightarrow$ Success.
3. Customer B attempts to apply code `EXCLUSIVE1` on a second order.
- **Visual Confirmation Checkpoint:**
  - System blocks Customer B with warning: `"This promotional code has reached its global redemption limit."`

---

### Workflow 8: Registering a Payment
1. Open the posted customer invoice from Workflow 2 ($550.00 total).
2. Click **Register Payment**.
3. In the modal dialog:
   - Journal: `Bank`
   - Payment Method: `Manual / Wire Transfer`
   - Amount: `$550.00`
   - Memo: `SUB-PAY-INV00001`
4. Click **Create Payment**.
- **Visual Confirmation Checkpoint:**
  - Green ribbon labeled **PAID** appears over the invoice.
  - Payment details widget displays date, journal, and reference.

---

### Workflow 9: Verifying Invoice Reconciliation
1. Navigate to **Accounting > Accounting > Journal Items**.
2. Filter by Partner: `Acme Global Enterprises`.
3. Locate the customer invoice line and payment line.
- **Visual Confirmation Checkpoint:**
  - The Accounts Receivable line displays a matching reconciliation identifier (e.g. `A1`).
  - Outstanding residual balance for the partner on this transaction is `$0.00`.

---

### Workflow 10: Checking Outstanding and Overdue Invoices
1. Navigate to **Invoicing > Customers > Invoices**.
2. Filter by search facet: **Unpaid**.
3. Select an invoice with `Due Date < Today` and filter by **Overdue**.
- **Visual Confirmation Checkpoint:**
  - Overdue invoices are highlighted with red text/badges.
  - Ageing bucket displays elapsed days past due (e.g., `12 days overdue`).

---

### Workflow 11: Viewing Dashboard KPIs
1. Click the top-level menu **Subscription Dashboard** (or Finance Dashboard).
2. Inspect the executive scorecards:
   - **Active Subscriptions:** Shows count of running contracts (e.g., `1`).
   - **Total Invoiced Revenue:** Displays cumulative posted invoice value (e.g., `$550.00`).
   - **Payments Received:** Displays actual collected cash (e.g., `$550.00`).
   - **Outstanding Receivables:** Displays unpaid invoice total.
- **Visual Confirmation Checkpoint:**
  - Metrics are cleanly divided between accrual invoiced totals and realized cash receipts.

---

### Workflow 12: Applying Dashboard Filters
1. Locate the dashboard filter bar on top:
   - Click **MTD** (Month-to-Date).
   - Click **YTD** (Year-to-Date).
   - Click **Filter by Partner Category** $\rightarrow$ `Enterprise`.
- **Visual Confirmation Checkpoint:**
  - Metric cards and chart widgets dynamically recalculate in under 1 second without a full page refresh.
