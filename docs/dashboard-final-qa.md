# Brightloop Subscription Management System — Dashboard Final Acceptance QA

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Acceptance Ready (Not Run)
- **Role:** Final QA Documentation & Acceptance Testing
- **Module:** `brightloop_dashboard`
- **Target ERP Platform:** Odoo 19

---

## Acceptance Test Protocol

For each test case below, the lead developer must execute the test in a running Odoo 19 instance, record the actual result, update the status (`Passed` or `Failed`), and attach the specified verification evidence.

---

### Test Case: ACC-DASH-001 — Active Subscriptions Metric Verification
- **Preconditions:** Database contains 100 total subscriptions:
  - 70 Active (running)
  - 10 Active (paused: `is_paused = True`)
  - 10 Quotations
  - 10 Closed contracts
- **Steps:**
  1. Open Subscription Dashboard.
  2. Inspect the "Active Subscriptions" KPI card.
- **Expected Result:**
  - Active Subscriptions card displays exactly `70`.
  - Paused, draft, quotation, and closed contracts are excluded from the primary active count.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of dashboard KPI card + SQL query count verifying 70 records.

---

### Test Case: ACC-DASH-002 — Invoiced Revenue vs Cash Received Segregation
- **Preconditions:**
  - 10 posted invoices for October totaling $10,000.00.
  - Registered payments collected: $6,500.00.
  - Open balance: $3,500.00.
- **Steps:**
  1. Open Dashboard filtered to October (MTD).
  2. Check "Total Invoiced Revenue" card.
  3. Check "Payments Received" card.
  4. Check "Outstanding Receivables" card.
- **Expected Result:**
  - Total Invoiced Revenue = `$10,000.00`
  - Payments Received = `$6,500.00`
  - Outstanding Receivables = `$3,500.00`
  - Accrual revenue and cash receipts are distinctly itemized.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of dashboard KPI cards side-by-side.

---

### Test Case: ACC-DASH-003 — Dynamic Temporal Filter Switching (MTD vs YTD)
- **Preconditions:** Invoices recorded across Jan ($5,000), Feb ($6,000), and March ($4,000). System date in March.
- **Steps:**
  1. Select filter "MTD" (Month-to-Date).
  2. Record displayed invoiced revenue.
  3. Switch filter to "YTD" (Year-to-Date).
  4. Record displayed invoiced revenue.
- **Expected Result:**
  - MTD displays: `$4,000.00`
  - YTD displays: `$15,000.00` ($5,000 + $6,000 + $4,000)
  - Transition executes smoothly within 1.0 second without page reload.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screen recording or two consecutive screenshots showing filter state and metric values.

---

### Test Case: ACC-DASH-004 — Overdue Aging Drill-Down Navigation
- **Preconditions:** 3 subscription invoices are past their due date.
- **Steps:**
  1. Click on the "Overdue Invoices" KPI card.
- **Expected Result:** System immediately opens the `account.move` tree view showing only the 3 delinquent invoices, pre-filtered with `[('invoice_date_due', '<', today), ('payment_state', '!=', 'paid'), ('state', '=', 'posted')]`.
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Screenshot of resulting pre-filtered list view after clicking KPI card.

---

### Test Case: ACC-DASH-005 — Query Latency Benchmark Under Load (<2.0s SLA)
- **Preconditions:** Test database loaded with synthetic benchmark dataset ($\ge 50,000$ subscriptions, $\ge 250,000$ invoices).
- **Steps:**
  1. Execute cold browser cache load of Subscription Dashboard.
  2. Measure server response time using Chrome DevTools Network tab or Odoo developer mode profiler.
- **Expected Result:** Total page load / API metric response time is **$< 2.00 \text{ seconds}$** (P95).
- **Actual Result:** 
- **Status:** Not Run
- **Evidence Required:** Network waterfall timeline screenshot or Odoo profiler flame graph demonstrating latency $<2.0$s.
