# Brightloop Subscription Management System — Discount Engine Specification

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Approved Baseline / Active
- **Module Ownership:** `brightloop_discount`, `brightloop_billing`, `brightloop_subscription`
- **Target ERP Platform:** Odoo 19 (Community/Enterprise)

---

## 1. Discount Architecture & Classification

The Brightloop discount engine governs promotional pricing, loyalty rebates, volume discounts, and introductory subscription incentives.

```mermaid
flowchart TD
    Inv[Subscription Invoicing Triggered] --> FindDisc[Lookup Active Discount Rules]
    
    FindDisc --> ValidateDates{Within Start & End Dates?}
    ValidateDates -- No --> Ignore[Do Not Apply Discount]
    
    ValidateDates -- Yes --> CheckLimits{Usage Limit Exhausted?}
    CheckLimits -- Yes: Total / Cust / Cycle limit hit --> Expire[Mark Discount Exhausted / Skip]
    
    CheckLimits -- No --> CheckMinVal{Meets Min Purchase Value & Min Qty?}
    CheckMinVal -- No --> SkipRule[Threshold Not Met / Skip]
    
    CheckMinVal -- Yes --> ScopeCheck{Discount Scope?}
    
    ScopeCheck -- Product Specific --> ApplyLine[Apply to Matching Product Lines Only]
    ScopeCheck -- Subscription Wide --> ApplyTotal[Apply to Entire Subscription Subtotal]
    
    ApplyLine --> ComputeType{Discount Computation Type?}
    ApplyTotal --> ComputeType
    
    ComputeType -- Percentage --> CalcPercent[D = Subtotal * Rate]
    ComputeType -- Fixed Amount --> CalcFixed[D = min(Fixed Amount, Subtotal)]
    
    CalcPercent --> RecordUsage[Increment Usage Counters & Cycle Count]
    CalcFixed --> RecordUsage
    
    RecordUsage --> ApplyToInvoice[Inject Discount Line into Customer Invoice]
```

---

## 2. Requirement Traceability Matrix

### 2.1 Discount Types & Eligibility Thresholds

| Req ID | Parameter / Scenario | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|---|
| **REQ-DISC-001** | **Percentage Discounts** | System must support percentage-based reductions ($0.01\%$ to $100.00\%$) on eligible subscription lines. | MGR | Discount calculation computes $\text{Discount} = \text{Base Price} \times \left(\frac{\text{Percent}}{100}\right)$. | `brightloop_discount` | 1. Percent must be $> 0$ and $\le 100$.<br>2. 100% discount results in zero line amount and bypasses payment gateway charge while generating valid zero-dollar accounting invoice.<br>3. Negative or $>100\%$ percentages rejected by database constraint. |
| **REQ-DISC-002** | **Fixed Amount Discounts** | System must support fixed currency deductions (e.g. $50.00 off per billing cycle). | MGR | System deducts fixed value from subtotal: $\text{Net} = \max(0, \text{Subtotal} - \text{Fixed Amount})$. | `brightloop_discount` | 1. Discount cannot exceed subtotal (net cannot be negative).<br>2. Fixed discounts in foreign currencies convert using current rate or fixed rate tables. |
| **REQ-DISC-003** | **Minimum Purchase Value Threshold** | Discounts may require a minimum invoice subtotal before becoming active (e.g. $20 off on orders over $150). | MGR, STAF | If `order_subtotal < min_purchase_value`, discount rule evaluates to zero reduction. | `brightloop_discount` | 1. Minimum purchase value validated against pre-tax subtotal.<br>2. Clear warning or line omission if cart/quote subtotal falls below threshold. |
| **REQ-DISC-004** | **Minimum Quantity Threshold** | Discounts may mandate a minimum subscription seat/unit volume (e.g. 15% off for 10+ user seats). | MGR, STAF | Discount evaluates line quantity against `min_quantity` threshold. | `brightloop_discount` | 1. Validation checked per eligible product line or cumulative subscription units.<br>2. Reducing seats below threshold on amendment immediately revokes discount. |

---

### 2.2 Temporal Windows & Usage Limits

| Req ID | Parameter / Scenario | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|---|
| **REQ-DISC-005** | **Validity Date Range (Start & End Dates)** | Discount rules must define valid calendar activation windows with exact date and time precision. | MGR | Discount is applied if and only if $\text{start\_date} \le \text{invoice\_date} \le \text{end\_date}$. | `brightloop_discount` | 1. Invoices generated before `start_date` or after `end_date` receive no discount.<br>2. Expired discounts display "Expired" status in configuration. |
| **REQ-DISC-006** | **Global Usage Limits** | Promotional campaigns must allow a global cap on total redemptions across the entire system (e.g. "First 500 customers"). | MGR | System increments `total_redemptions_count`; when count equals `max_global_redemptions`, discount is disabled for future quotes. | `brightloop_discount` | 1. Redemptions tracked atomically to prevent race condition over-allocations.<br>2. Existing active subscriptions that already locked the discount remain honored according to plan rules. |
| **REQ-DISC-007** | **Customer Redemption Limits** | Discounts can restrict redemptions per individual customer account (e.g. one promotional coupon per customer). | MGR, CUST | System checks redemption history on partner record: $\text{count}(\text{partner\_id}) < \text{max\_per\_customer}$. | `brightloop_discount` | 1. Re-using same promo code on new subscription by same partner rejected with validation message: `"You have already redeemed this promotional discount."` |
| **REQ-DISC-008** | **Billing Cycle Limits (Introductory Pricing)** | Discounts can be restricted to a specific number of consecutive recurring billing cycles (e.g. "50% off for first 3 months"). | MGR, STAF | System tracks `cycles_applied_count` on subscription line; once count equals `max_cycles`, discount auto-terminates. | `brightloop_discount`, `brightloop_billing` | 1. Automatically applies to Cycles 1, 2, and 3.<br>2. Cycle 4 invoice automatically reverts to standard catalog pricing without requiring manual staff intervention.<br>3. Chatter logs discount exhaustion notice. |

---

### 2.3 Scope, Automatic Recurrence & Boundary Rules

| Req ID | Parameter / Scenario | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|---|
| **REQ-DISC-009** | **Product-Specific vs Subscription-Wide Scope** | Discounts must support targeting either specific product catalog IDs or the cumulative subscription total. | MGR | Product-specific discount applies only to matching line items; subscription-wide applies as a bottom-line invoice adjustment. | `brightloop_discount` | 1. Line-level discounts adjust line net price.<br>2. Order-level discounts generate dedicated negative adjustment invoice line mapped to promotional expense account. |
| **REQ-DISC-010** | **Automatic Recurring Application** | An active subscription discount must persist across recurring billing cycles as long as validity conditions hold. | SYSTEM (Cron) | Recurring invoice generator automatically copies qualifying discount rules from subscription to generated invoice. | `brightloop_discount`, `brightloop_billing` | 1. No manual re-entry required per cycle.<br>2. Each application increments the cycle counter. |
| **REQ-DISC-011** | **Expiration on Exact Billing Date Boundary** | If a discount expires on `2026-11-30 23:59:59` and invoice is generated on `2026-11-30`, discount must be applied; if generated on `2026-12-01`, discount is excluded. | SYSTEM (Cron) | Date comparison evaluates timestamps inclusively at date level: `invoice_date <= discount.end_date`. | `brightloop_discount` | 1. Billing date exactly on end date receives discount.<br>2. Billing date 1 day after end date drops discount cleanly. |
| **REQ-DISC-012** | **Discount Stacking & Priority** | Multiple discounts applied to the same subscription must follow explicit precedence (Non-stackable vs Stackable). | MGR | Non-stackable discounts override standard discounts; stackable discounts compute compound or sequential deductions. | `brightloop_discount` | 1. By default, discount rules are mutually exclusive (highest savings wins).<br>2. If stackable flag is set, percentage is applied sequentially or additively as configured. |
