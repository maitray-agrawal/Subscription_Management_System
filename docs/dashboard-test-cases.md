# Brightloop Subscription Management System — Dashboard QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Execution (Not Run)
- **Scope:** Functional verification of executive KPIs, date-range filters, multi-currency conversions, status grouping, and drill-down navigation.
- **Traceability:** Maps directly to `docs/dashboard-kpi-definitions.md`.

---

## 1. Test Suite Summary

| Category Code | Functional Area | Normal | Boundary | Negative | Permission | Total Test Cases |
|---|---|---|---|---|---|---|
| **TC-DASH-KPI** | Core KPI Calculation Accuracy | 4 | 2 | 1 | 0 | 7 |
| **TC-DASH-FILT**| Date Range & Category Filtering | 3 | 2 | 1 | 0 | 6 |
| **TC-DASH-DRILL**| Drill-Down & Status Grouping | 2 | 1 | 0 | 1 | 4 |
| **TC-DASH-CURR**| Multi-Currency Aggregation | 2 | 1 | 1 | 0 | 4 |
| **Total** | | **11** | **6** | **3** | **1** | **21** |

---

## 2. Test Cases

### 2.1 Core KPI Calculation Accuracy (TC-DASH-KPI)

#### TC-DASH-001 (Normal): Invoiced Revenue vs Cash Received Verification
- **Traceability:** KPI-02, KPI-04
- **Test Type:** Normal
- **Preconditions:**
  - 10 active subscriptions billed on Oct 1 @ $1,000.00 each ($10,000 invoiced total).
  - 6 customers paid in full ($6,000.00 cash).
  - 4 customers have not paid ($0.00 cash).
- **Execution Steps:**
  1. Open Finance Dashboard for October.
  2. Inspect "Total Invoiced Revenue" card.
  3. Inspect "Payments Received" card.
  4. Inspect "Outstanding Receivables" card.
- **Expected Result:**
  - Total Invoiced Revenue displays: `$10,000.00`
  - Payments Received displays: `$6,000.00`
  - Outstanding Receivables displays: `$4,000.00`
  - The system does NOT treat invoiced revenue and payments received as the same metric.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DASH-002 (Normal): Overdue Invoices Aging Segregation
- **Traceability:** KPI-06
- **Test Type:** Normal
- **Preconditions:**
  - Invoice A ($1,000) posted Oct 1, due Oct 15 (Simulated Date: Oct 25 $\implies$ 10 days overdue).
  - Invoice B ($2,000) posted Oct 15, due Oct 30 (Simulated Date: Oct 25 $\implies$ Not overdue).
- **Execution Steps:**
  1. View Overdue Invoices widget on dashboard.
- **Expected Result:**
  - Overdue Invoices displays: `$1,000.00` (1 invoice).
  - Invoice B is excluded from overdue count (remains under Outstanding Current).
- **Actual Result:** 
- **Status:** Not Run

#### TC-DASH-003 (Boundary): Zero Data Cold-Start Dashboard Render
- **Traceability:** KPI-01 through KPI-07
- **Test Type:** Boundary
- **Preconditions:** Brand new company database with zero subscriptions and zero invoices.
- **Execution Steps:**
  1. Navigate to Subscription Dashboard.
- **Expected Result:**
  - Dashboard loads cleanly without division-by-zero or `TypeError: null` exceptions.
  - All monetary cards display `$0.00`; contract count displays `0`.
  - Placeholder graphics appear: "No subscription data available for this period."
- **Actual Result:** 
- **Status:** Not Run

#### TC-DASH-004 (Negative): Draft and Cancelled Invoices Excluded from Revenue
- **Traceability:** KPI-02, KPI-03
- **Test Type:** Negative
- **Preconditions:**
  - 1 posted invoice @ $500.00.
  - 1 draft invoice @ $500.00.
  - 1 cancelled invoice @ $500.00.
- **Execution Steps:**
  1. Check Total Invoiced Revenue KPI.
- **Expected Result:** Invoiced Revenue displays exactly `$500.00`; draft and cancelled invoices are strictly excluded.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.2 Date Range & Category Filtering (TC-DASH-FILT)

#### TC-DASH-005 (Normal): Dynamic Filter Slicing (MTD vs YTD)
- **Traceability:** KPI-02, KPI-04
- **Test Type:** Normal
- **Preconditions:** Invoices posted across Jan, Feb, and March ($1,000 each month). Current date: March 15.
- **Execution Steps:**
  1. Select filter "Month-to-Date" (MTD).
  2. Select filter "Year-to-Date" (YTD).
- **Expected Result:**
  - MTD displays: `$1,000.00` (March only).
  - YTD displays: `$3,000.00` (Jan + Feb + March).
  - Re-render occurs within 500 ms without full-page reload.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DASH-006 (Boundary): Custom Leap Day Date Range (Feb 29)
- **Traceability:** KPI-02
- **Test Type:** Boundary
- **Preconditions:** Leap year 2028. Invoices generated on `2028-02-28`, `2028-02-29`, and `2028-03-01` ($100 each).
- **Test Data:** Date filter: `2028-02-29` to `2028-02-29`.
- **Execution Steps:**
  1. Apply single-day date filter for Feb 29, 2028.
- **Expected Result:** System correctly identifies leap date; displays exactly `$100.00`.
- **Actual Result:** 
- **Status:** Not Run

---

### 2.3 Drill-Down & Permissions (TC-DASH-DRILL)

#### TC-DASH-007 (Normal): One-Click Drill-Down into Overdue Invoices
- **Traceability:** KPI-06
- **Test Type:** Normal
- **Preconditions:** Dashboard displays 5 overdue invoices.
- **Test Data:** Click event on "Overdue Invoices" scorecard.
- **Execution Steps:**
  1. Click on the Overdue Invoices KPI card.
- **Expected Result:** System navigates to `account.move` tree view pre-filtered with domain `[('invoice_date_due', '<', today), ('payment_state', '!=', 'paid'), ('state', '=', 'posted')]`.
- **Actual Result:** 
- **Status:** Not Run

#### TC-DASH-008 (Permission): Evaluator Role Restricted Dashboard View
- **Traceability:** REQ-SUB-003, KPI-01
- **Test Type:** Permission
- **Preconditions:** Evaluator user logged in.
- **Execution Steps:**
  1. Evaluator accesses Dashboard.
- **Expected Result:** Real corporate financial figures are masked or sanitized; evaluator cannot drill down to view sensitive customer bank accounts or invoices.
- **Actual Result:** 
- **Status:** Not Run
