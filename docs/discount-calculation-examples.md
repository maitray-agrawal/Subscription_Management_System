# Brightloop Subscription Management System — Discount Calculation Worked Examples

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Approved Baseline / Active
- **Module Ownership:** `brightloop_discount`, `brightloop_billing`
- **Target ERP Platform:** Odoo 19 (Community/Enterprise)

---

## 1. Overview & Calculation Conventions

All discount calculations in Brightloop adhere to the following business conventions:
- **Calculation Base:** Discounts are calculated on pre-tax line subtotals unless explicitly configured otherwise.
- **Rounding Rule:** Line amounts and intermediate discounts are rounded using half-up arithmetic (`ROUND_HALF_UP`) according to the active currency precision (e.g., $0.01 for USD, EUR, GBP).
- **Floor Limit:** Net payable line or invoice amount cannot be negative ($\ge \$0.00$).

---

## 2. Worked Calculation Scenarios

### Scenario 1: Standard Percentage Discount (Single Line)
- **Product:** Brightloop SaaS Starter (Monthly)
- **Catalog Unit Price:** $80.00
- **Quantity:** 5 seats
- **Tax:** 10% GST (Tax-Exclusive)
- **Discount:** 15% off coupon (`SUMMER15`)

$$\text{Gross Subtotal} = 5 \times \$80.00 = \$400.00$$
$$\text{Discount Amount} = \$400.00 \times 0.15 = \$60.00$$
$$\text{Net Untaxed Subtotal} = \$400.00 - \$60.00 = \$340.00$$
$$\text{Tax (10\%)} = \$340.00 \times 0.10 = \$34.00$$
$$\mathbf{\text{Total Invoiced Amount}} = \$340.00 + \$34.00 = \mathbf{\$374.00}$$

---

### Scenario 2: Fixed Amount Discount with Multi-Line Distribution
- **Subscription Lines:**
  - Line 1: 10 $\times$ Enterprise Core @ $100.00 = $1,000.00
  - Line 2: 2 $\times$ Premium Support @ $250.00 = $500.00
- **Order Subtotal:** $1,500.00
- **Discount:** $300.00 Fixed Voucher (`VOUCHER300`)
- **Distribution Method:** Proportionate line distribution

$$\text{Line 1 Ratio} = \frac{\$1,000.00}{\$1,500.00} = 66.6667\% \implies \text{Line 1 Discount} = \$300.00 \times \frac{2}{3} = \$200.00$$
$$\text{Line 2 Ratio} = \frac{\$500.00}{\$1,500.00} = 33.3333\% \implies \text{Line 2 Discount} = \$300.00 \times \frac{1}{3} = \$100.00$$

$$\text{Line 1 Net} = \$1,000.00 - \$200.00 = \$800.00$$
$$\text{Line 2 Net} = \$500.00 - \$100.00 = \$400.00$$
$$\mathbf{\text{Net Invoice Total (Pre-Tax)}} = \$800.00 + \$400.00 = \mathbf{\$1,200.00}$$

---

### Scenario 3: Introductory 3-Cycle Discount Lifecycle
- **Product:** Monthly Analytics Plan ($200.00 / month)
- **Discount Rule:** "50% off for the first 3 billing cycles" (`INTRO50`, `max_cycles = 3`)
- **Billing Progression:**

| Cycle # | Billing Date | Catalog Price | Discount % | Discount ($) | Invoiced Net | Cycle Counter | Status |
|---|---|---|---|---|---|---|---|
| **Cycle 1** | 2026-11-01 | $200.00 | 50% | -$100.00 | **$100.00** | 1 / 3 | Active |
| **Cycle 2** | 2026-12-01 | $200.00 | 50% | -$100.00 | **$100.00** | 2 / 3 | Active |
| **Cycle 3** | 2027-01-01 | $200.00 | 50% | -$100.00 | **$100.00** | 3 / 3 | Active (Final) |
| **Cycle 4** | 2027-02-01 | $200.00 | 0% | $0.00 | **$200.00** | 3 / 3 | **Exhausted** |
| **Cycle 5** | 2027-03-01 | $200.00 | 0% | $0.00 | **$200.00** | 3 / 3 | Exhausted |

*Result:* On Cycle 4, the discount engine detects `cycles_applied_count >= max_cycles` and cleanly omits the discount line, restoring full billing without customer disruption.

---

### Scenario 4: Minimum Quantity Threshold Failure & Re-qualification
- **Discount Rule:** `BULK20` = 20% off when ordering $\ge 10$ seats.
- **Seat Price:** $50.00 / seat / month.

#### Case A: Initial Order with 12 Seats (Eligible)
$$\text{Gross} = 12 \times \$50.00 = \$600.00$$
$$\text{Threshold Check:} \quad 12 \ge 10 \implies \text{Eligible (True)}$$
$$\text{Discount} = \$600.00 \times 0.20 = \$120.00$$
$$\mathbf{\text{Net Subtotal}} = \mathbf{\$480.00} \quad (\$40.00 / \text{seat effective})$$

#### Case B: Mid-Term Contract Amendment: Downgrade to 8 Seats (Ineligible)
$$\text{Gross} = 8 \times \$50.00 = \$400.00$$
$$\text{Threshold Check:} \quad 8 \ge 10 \implies \text{Ineligible (False)}$$
$$\text{Discount} = \$0.00$$
$$\mathbf{\text{Net Subtotal}} = \mathbf{\$400.00} \quad (\$50.00 / \text{seat standard})$$

---

### Scenario 5: Discount Stacking (Volume + Seasonal Coupon)
- **Base Subtotal:** $1,000.00
- **Rule 1 (Volume Rebate):** 10% off (Stackable)
- **Rule 2 (Black Friday Promo):** 15% off (Stackable)
- **Compounding Method (Standard):** Sequential multiplicative deduction

$$\text{Step 1: Apply Volume Rebate} = \$1,000.00 \times 0.10 = \$100.00 \implies \text{Balance} = \$900.00$$
$$\text{Step 2: Apply Promo on Net Balance} = \$900.00 \times 0.15 = \$135.00 \implies \text{Final Net} = \$765.00$$
$$\text{Total Effective Discount} = \$100.00 + \$135.00 = \$235.00 \quad (23.5\% \text{ effective savings})$$
$$\mathbf{\text{Total Invoiced (Pre-Tax)}} = \mathbf{\$765.00}$$
