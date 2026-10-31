# Brightloop Subscription Management System — Dashboard Performance Acceptance Criteria

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Approved Baseline / Active
- **Module Ownership:** `brightloop_dashboard`, `brightloop_billing`
- **Target ERP Platform:** Odoo 19 (PostgreSQL 15+)
- **Verification Rule:** Performance requirements must **NEVER** be claimed as achieved without documented runtime benchmark evidence provided by the lead developer.

---

## 1. Core Performance Service Level Agreements (SLAs)

| Operation | Scale Baseline | Maximum Allowable Latency | Target Latency | Pass/Fail Condition |
|---|---|---|---|---|
| **Initial Dashboard Load (Cold Cache)** | 50,000 subscriptions, 250,000 invoices | **$< 2.00 \text{ seconds}$** | $< 1.20 \text{ s}$ | P95 Latency over 20 repeated runs |
| **Initial Dashboard Load (Warm Cache)** | 50,000 subscriptions, 250,000 invoices | **$< 0.80 \text{ seconds}$** | $< 0.40 \text{ s}$ | P95 Latency over 20 repeated runs |
| **Temporal Filter Switch (e.g. MTD to YTD)** | 250,000 invoices | **$< 1.00 \text{ second}$** | $< 0.50 \text{ s}$ | Client reactive render without page reload |
| **Status Grouping / Pivot Breakdown** | 50,000 subscriptions | **$< 1.50 \text{ seconds}$** | $< 0.75 \text{ s}$ | ORM `read_group` aggregation |
| **Drill-Down to Filtered Invoice Tree** | 10,000 filtered records | **$< 1.20 \text{ seconds}$** | $< 0.60 \text{ s}$ | Server pagination (80 records/page) |

---

## 2. Architectural Guidelines & Optimization Requirements

To guarantee the $<2.0$ second performance threshold under enterprise volume, the lead developer must implement the following architectural optimizations:

### 2.1 Database Indexing Requirements

PostgreSQL composite indexes must be defined in addon setup (`brightloop_billing/models/account_move.py` or SQL migration scripts):

```sql
-- Index for Invoiced Revenue & Temporal Range Filtering
CREATE INDEX IF NOT EXISTS idx_account_move_sub_revenue
ON account_move (move_type, state, subscription_id, invoice_date)
WHERE state = 'posted' AND move_type = 'out_invoice';

-- Index for Overdue Aging & Receivables
CREATE INDEX IF NOT EXISTS idx_account_move_overdue_aging
ON account_move (state, payment_state, invoice_date_due, subscription_id)
WHERE state = 'posted' AND payment_state IN ('not_paid', 'partial');

-- Index for Subscription Status Aggregations
CREATE INDEX IF NOT EXISTS idx_subscription_state_active
ON brightloop_subscription (state, is_paused, date_start, commitment_end_date);
```

### 2.2 Materialized Reporting View / Pre-Aggregation

Direct sequential scans over raw `account_move_line` tables must be avoided for high-volume dashboard rendering.
- Recommendation: Utilize an automated SQL Materialized View (`brightloop.subscription.dashboard.report`) refreshed incrementally via an hourly background cron.
- The dashboard frontend should query the pre-aggregated summary table for multi-month trends rather than executing real-time full-table sums.

---

## 3. Synthetic Benchmark Protocol for Lead Developer

Before signing off on Stage 7 performance compliance, the lead developer must execute and document the following synthetic load test:

### Benchmark Test Harness

1. **Test Fixture Generation:**
   - Seed database with:
     - 50,000 `brightloop.subscription` records (70% Active, 15% Closed, 10% Quotation, 5% Draft/Paused).
     - 250,000 posted `account.move` customer invoices linked to subscriptions.
     - 200,000 reconciled `account.payment` records.
2. **Measurement Script:**
   - Execute 50 automated HTTP GET / RPC requests simulating 10 concurrent finance managers loading the dashboard.
   - Record response times using Python `time.perf_counter()` or Odoo `pg_stat_statements`.
3. **Evidence Submission Template:**

```markdown
### Lead Developer Benchmark Sign-off Evidence
- Date of Test: [YYYY-MM-DD]
- Environment: CPU Cores: [X], RAM: [X GB], PostgreSQL Version: [X]
- Database Size: Subscriptions: [X], Invoices: [X]
- Cold Cache Load P95: [X.XX seconds] (Must be < 2.0s)
- Warm Cache Load P95: [X.XX seconds] (Must be < 0.8s)
- MTD to YTD Filter Switch: [X.XX seconds] (Must be < 1.0s)
- Query Execution Plan: [EXPLAIN ANALYZE output attached]
- Developer Sign-Off: [Name]
```

> [!CAUTION]
> The Documentation and QA specialist cannot execute runtime Odoo benchmarks. The dashboard status will remain **"Performance Verification Pending"** until the lead developer provides the signed benchmark evidence above.
