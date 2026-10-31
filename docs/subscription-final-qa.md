# Brightloop Subscription Management System — Subscription Acceptance QA Checklist

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Test Ready (Not Run — Execution reserved for Lead Developer)
- **Scope:** Complete end-to-end acceptance checklist for subscription models, plans, variants, quotations, and lifecycle workflows.
- **Traceability:** Maps to Assignment Section 3 (*"A Month at Brightloop"*).
- **Author:** Subscription & Customer Portal QA Specialist

---

## Acceptance Testing Checklist

| Test ID | Scenario Description | Preconditions | Test Data & Steps | Expected Result | Actual Result | Status | Required Evidence |
|---|---|---|---|---|---|---|---|
| **ACC-SUB-001** | Create Product with Brand Variant (+560) | Logged in as Admin | 1. Name: `Brightloop Core`<br>2. Type: Service<br>3. Sales Price: 1000.00<br>4. Add Attribute: Brand<br>5. Add Value: `Odoo` (Extra: 560.00)<br>6. Save | 1. 2 variants generated (`Standard` @ 1000, `Odoo` @ 1560).<br>2. `is_subscription_product = True`. | | Not Run | Screenshot of Product Variant List showing prices |
| **ACC-SUB-002** | Create Daily Billing Plan with Auto-Close | Logged in as Admin | 1. Name: `Daily Trial`<br>2. Billing Interval: 1 Day<br>3. Min Quantity: 1<br>4. Auto-close: Yes<br>5. Allow Pause: Yes<br>6. Allow Renew: Yes | 1. Plan saved with Daily recurrence.<br>2. Recurrence displays as "1 Day" or "Daily". | | Not Run | Screenshot of Subscription Plan form |
| **ACC-SUB-003** | Create Monthly Plan with Min Quantity Enforcement | Logged in as Admin | 1. Name: `Team Monthly`<br>2. Billing: 1 Month<br>3. Min Quantity: 5 seats<br>4. Save | 1. Plan saved.<br>2. Minimum quantity validation active on quotation lines. | | Not Run | Screenshot of Plan form showing Min Qty = 5 |
| **ACC-SUB-004** | Create Quotation Template with Lines & Validity | Logged in as Admin | 1. Name: `Enterprise Pack`<br>2. Plan: `Team Monthly`<br>3. Validity: 30 days<br>4. Add Line: `Brightloop Core (Brand: Odoo)` Qty: 5 | 1. Template created.<br>2. Line defaults to unit price 1560.00 and qty 5. | | Not Run | Screenshot of Quotation Template form |
| **ACC-SUB-005** | Generate Quotation from Template | Logged in as Staff | 1. Open Subscriptions > Quotations > New.<br>2. Select Customer `Deco Addict`.<br>3. Select Template `Enterprise Pack`. | 1. Plan and product lines auto-populate.<br>2. Expiration date set to today + 30 days.<br>3. State = `Draft`. | | Not Run | Screenshot of Subscription form with populated lines |
| **ACC-SUB-006** | Transition Draft to Quotation | Logged in as Staff | 1. Open Draft subscription.<br>2. Click **Create Quotation**.<br>3. Check state and sequence. | 1. Unique sequence generated (e.g. `SUB/2026/00001`).<br>2. State transitions to `Quotation`. | | Not Run | Screenshot showing state `Quotation` and sequence |
| **ACC-SUB-007** | Enforce Minimum Quantity Constraint | Logged in as Staff | 1. On `Team Monthly` subscription (MOQ = 5), edit line quantity to 3.<br>2. Attempt to confirm quotation. | 1. System blocks confirmation.<br>2. Validation error: *"Quantity must be at least 5 for plan Team Monthly"*. | | Not Run | Error dialog screenshot |
| **ACC-SUB-008** | Confirm Subscription | Logged in as Staff or Customer | 1. Set quantity = 5.<br>2. Click **Confirm**. | 1. State transitions from `Quotation` to `Confirmed`.<br>2. Chatter logs confirmation user and timestamp. | | Not Run | Screenshot showing state `Confirmed` |
| **ACC-SUB-009** | Activate Subscription & Schedule Billing | Logged in as Staff | 1. Open Confirmed subscription.<br>2. Click **Activate**. | 1. State transitions to `Active`.<br>2. `start_date` set to today.<br>3. `next_billing_date` scheduled accurately based on plan recurrence. | | Not Run | Screenshot showing state `Active` and Next Billing Date |
| **ACC-SUB-010** | Pause and Resume Active Subscription | Logged in as Staff | 1. On Active subscription, click **Pause**.<br>2. Verify `is_paused = True`.<br>3. Click **Resume**.<br>4. Verify active status resumed. | 1. Pause pauses recurring billing.<br>2. Resume reactivates billing pointer.<br>3. State tracking recorded in chatter. | | Not Run | Chatter audit trail screenshot |
| **ACC-SUB-011** | Early Closure Verification | Logged in as Staff | 1. On plan with `allow_early_closure = True`, click **Close Subscription**.<br>2. On plan with `allow_early_closure = False`, verify button is hidden/disabled. | 1. Plan permissions respected.<br>2. State moves to `Closed`. | | Not Run | State transition screenshot |
| **ACC-SUB-012** | Subscription Renewal Workflow | Logged in as Staff | 1. On an Active or Closed subscription, click **Renew**.<br>2. Inspect new contract/period. | 1. Renewal contract or extended term generated.<br>2. Links back to original contract reference. | | Not Run | Renewal contract screenshot |
