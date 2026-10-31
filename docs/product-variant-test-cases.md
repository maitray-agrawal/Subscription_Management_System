# Brightloop Subscription Management System — Product & Variant QA Test Cases

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Lead Developer Implementation
- **Functional Scope:** Product definitions, product types, sales & cost prices, notes, multi-variant attributes, and variant-specific price surcharges (e.g., Brand attribute with "Odoo" adding +560).
- **Target Platform:** Odoo 19 Enterprise / Community
- **Author:** Subscription & Customer Portal QA Specialist

---

## 1. Product & Variant Acceptance Criteria & Requirements Mapping

Derived directly from Assignment Section 3 (*"Launching a new plan"*):
> *"Brightloop is launching a new product. The admin adds it with its name, type, sales price, cost price and notes, and offers it in variants, for example by brand, where choosing the Odoo brand adds 560 to the price."*

| Feature | Acceptance Criteria |
|---|---|
| **Product Fields** | Admin can create products with Name, Product Type (`service` for subscriptions), Sales Price, Cost Price, and Internal Notes. |
| **Recurring Flag** | Product has a dedicated subscription flag (`recurring_invoice` / `is_subscription_product = True`) ensuring it can be used on subscription plans. |
| **Attribute Setup** | Admin can configure attributes (e.g., "Brand", "Tier", "Seats") and attribute values. |
| **Price Extra Surcharge** | Attribute values support a price surcharge (`price_extra`). Specifically, choosing Brand: "Odoo" adds 560.00 to the product base sales price. |
| **Quotation Dynamic Pricing** | When sales staff select a variant on a subscription quotation line, the unit price dynamically defaults to:$$\text{Line Unit Price} = \text{Base Sales Price} + \sum \text{Variant Price Extras}$$ |
| **Permission Controls** | Only Administrator (`group_brightloop_admin`) can create/edit products and price extras. Internal Staff (`group_brightloop_user`) can select variants on quotations. |

---

## 2. Test Suite Summary

| Test Case ID | Test Category | Title | Priority |
|---|---|---|---|
| **TC-PV-001** | Normal | Create Standard Subscription Product with Full Metadata | High |
| **TC-PV-002** | Normal | Configure "Brand" Attribute with "Odoo" (+560) Price Extra | Critical |
| **TC-PV-003** | Normal | Dynamic Unit Price Resolution on Subscription Quotation | Critical |
| **TC-PV-004** | Boundary | Multi-Attribute Combinations (Brand + Hosting Tier) | High |
| **TC-PV-005** | Boundary | Zero Base Price with Attribute Surcharge | Medium |
| **TC-PV-006** | Negative | Prohibit Incomplete Variant Configuration on Quotations | Medium |
| **TC-PV-007** | Permission | Restrict Product & Price Extra Management to Administrators | High |

---

## 3. Detailed Test Scenarios

### TC-PV-001 (Normal): Create Standard Subscription Product with Full Metadata
- **Objective:** Verify creation of base subscription service product with name, type, sales price, cost price, and notes.
- **Preconditions:** Logged in as Administrator (`group_brightloop_admin`).
- **Test Data:**
  - Product Name: `Brightloop Enterprise Suite`
  - Product Type: `Service`
  - Sales Price: `1200.00`
  - Cost Price: `400.00`
  - Internal Notes: `Flagship multi-tenant ERP subscription core.`
  - Recurring Flag: `True`
- **Execution Steps:**
  1. Navigate to **Subscriptions > Products > Products**.
  2. Click **New**.
  3. Enter Name, Type (`Service`), Sales Price (`1200.00`), Cost (`400.00`), and Internal Notes.
  4. Ensure `Can be Subscribed` / recurring toggle is checked.
  5. Click **Save**.
- **Expected Result:** Product template is saved successfully with active status; sales and cost prices persist accurately without rounding errors; product is marked as a subscription service.
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run

---

### TC-PV-002 (Normal): Configure "Brand" Attribute with "Odoo" (+560) Price Extra
- **Objective:** Verify adding attribute "Brand" with value "Odoo" that adds +560.00 to the base price.
- **Preconditions:** Product `Brightloop Enterprise Suite` created (base price: 1200.00). Logged in as Administrator.
- **Test Data:**
  - Attribute: `Brand`
  - Attribute Values:
    - `Standard`: Price Extra = `0.00`
    - `Odoo`: Price Extra = `560.00`
    - `Custom White-Label`: Price Extra = `1200.00`
- **Execution Steps:**
  1. Open product form for `Brightloop Enterprise Suite`.
  2. Navigate to **Attributes & Variants** tab.
  3. Add a line: Attribute = `Brand`.
  4. In Values, add `Standard` (Extra Price = 0), `Odoo` (Extra Price = 560.00), and `Custom White-Label` (Extra Price = 1200.00).
  5. Save product record.
  6. Click the **Product Variants** smart button on the header.
- **Expected Result:** 
  1. System generates 3 distinct `product.product` variant records.
  2. The variant with `Brand: Standard` has effective sales price = 1200.00.
  3. The variant with `Brand: Odoo` has effective sales price = 1760.00 ($1200 + 560$).
  4. The variant with `Brand: Custom White-Label` has effective sales price = 2400.00 ($1200 + 1200$).
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run

---

### TC-PV-003 (Normal): Dynamic Unit Price Resolution on Subscription Quotation
- **Objective:** Verify that selecting the "Odoo" brand variant dynamically pulls $1760.00 on a subscription quotation line.
- **Preconditions:** Variants from TC-PV-002 created. Logged in as Internal Staff (`group_brightloop_user`).
- **Test Data:** Customer: `Azure Interior`, Product: `Brightloop Enterprise Suite (Brand: Odoo)`, Qty: 2.
- **Execution Steps:**
  1. Navigate to **Subscriptions > Quotations > New**.
  2. Select Customer `Azure Interior` and Plan `Monthly Standard`.
  3. Under Subscription Lines, click **Add a line**.
  4. Select product `Brightloop Enterprise Suite (Brand: Odoo)`.
  5. Set quantity = 2.
- **Expected Result:**
  1. Line unit price automatically populates as `1760.00`.
  2. Subtotal calculates as $2 \times 1760.00 = 3520.00$.
  3. Taxes (if applicable) compute against the 3520.00 subtotal.
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run

---

### TC-PV-004 (Boundary): Multi-Attribute Combinations (Brand + Hosting Tier)
- **Objective:** Verify cumulative price extra calculation with multiple variant dimensions.
- **Preconditions:** Logged in as Administrator.
- **Test Data:**
  - Base Product: `Brightloop Analytics` (Base Price = 500.00).
  - Attribute 1: `Brand` -> Value `Odoo` (Price Extra = +560.00).
  - Attribute 2: `Hosting` -> Value `Dedicated Cloud` (Price Extra = +350.00).
- **Execution Steps:**
  1. Configure both attributes and values on `Brightloop Analytics`.
  2. Open the variant combination `Brand: Odoo, Hosting: Dedicated Cloud`.
  3. Check effective list price.
- **Expected Result:** Effective price is exactly $500.00 + 560.00 + 350.00 = 1410.00$.
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run

---

### TC-PV-005 (Boundary): Zero Base Price with Attribute Surcharge
- **Objective:** Verify price extra behavior when base product price is 0.00 (freemium/add-on base).
- **Preconditions:** Logged in as Administrator.
- **Test Data:**
  - Base Product: `Community Connector` (Base Price = 0.00).
  - Attribute: `Brand` -> Value `Odoo` (Price Extra = +560.00).
- **Execution Steps:**
  1. Create product with Sales Price = 0.00.
  2. Add attribute Brand: Odoo (+560.00).
  3. Add product to quotation line.
- **Expected Result:** Unit price on line resolves cleanly to 560.00 without division by zero or validation crash.
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run

---

### TC-PV-006 (Negative): Prohibit Incomplete Variant Configuration on Quotations
- **Objective:** Ensure staff cannot confirm a quotation with a generic template that requires an unselected variant.
- **Preconditions:** Product has variants configured. Logged in as Internal Staff.
- **Execution Steps:**
  1. Attempt to add a subscription line with the template parent without selecting the specific variant.
- **Expected Result:** UI/ORM forces variant selection or defaults to the primary variant; invalid or null product_id cannot be saved.
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run

---

### TC-PV-007 (Permission): Restrict Product & Price Extra Management to Administrators
- **Objective:** Verify that Internal Staff cannot modify product catalog pricing or attribute surcharges.
- **Preconditions:** User `staff_user` with `group_brightloop_user` only.
- **Execution Steps:**
  1. Log in as `staff_user`.
  2. Attempt to open product configuration to change the Odoo brand price extra from 560 to 100.
  3. Attempt to save the change.
- **Expected Result:** Fields are readonly or system raises an `AccessError`; internal staff cannot modify catalog prices or attribute extra costs.
- **Actual Result:** *(To be executed by Lead Developer)*
- **Status:** Not Run
