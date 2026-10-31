# Brightloop Subscription Management System — Access Control & Customer Access Matrix

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Baseline Ready for Verification
- **Purpose:** Defines granular CRUD permissions and record-level boundary rules across all user roles.
- **Traceability:** Assignment Section 3 (*"Not everyone who logs in should see the same things..."*) and Stage 2 Security implementation.
- **Author:** Subscription & Customer Portal QA Specialist

---

## 1. Role Definitions

| Role | Technical Group Name | Parent / Implied Group | Description |
|---|---|---|---|
| **Public Visitor** | *(No Group)* | Public Session | Unauthenticated web visitor. Can only view public website and signup. |
| **Customer** | `brightloop_base.group_brightloop_portal` | `base.group_portal` | External registered customer. Access restricted exclusively to own records via portal. |
| **Internal Staff** | `brightloop_base.group_brightloop_user` | `base.group_user` | Operational staff. Handles day-to-day quotations, subscriptions, and payment receipts. |
| **Administrator** | `brightloop_base.group_brightloop_admin` | `group_brightloop_user`, `base.group_system` | Full executive and technical control. Exclusively manages staff, plans, and discounts. |

---

## 2. Granular Entity Access Matrix

| Entity / Resource | Public Visitor | Customer (Portal) | Internal Staff | Administrator |
|---|:---:|:---:|:---:|:---:|
| **Public Signup (`/web/signup`)** | Create | View | View | View |
| **Product Templates (`product.template`)** | No Access | No Access | Read Only | Full CRUD |
| **Product Variants (`product.product`)** | No Access | Read Only (via lines) | Read Only | Full CRUD |
| **Attribute Price Extras (`product.attribute`)**| No Access | No Access | Read Only | Full CRUD |
| **Subscription Plans (`brightloop.subscription.plan`)** | No Access | No Access | Read Only | Full CRUD |
| **Quotation Templates (`brightloop.quotation.template`)** | No Access | No Access | Read / Use | Full CRUD |
| **Customer Subscriptions (Own Records)** | No Access | Read Only (Portal) | Full CRUD | Full CRUD |
| **Customer Subscriptions (Other Customers)** | **No Access** | **Strictly Forbidden** | Full CRUD | Full CRUD |
| **Customer Invoices (Own Records)** | No Access | Read Only / PDF | Read / Confirm / Pay | Full CRUD |
| **Customer Invoices (Other Customers)** | **No Access** | **Strictly Forbidden** | Read / Confirm / Pay | Full CRUD |
| **Customer Payment Registration (`account.payment`)**| No Access | No Access (auto-tracked) | Create / Reconcile | Full CRUD |
| **Discount Rules (`brightloop.discount.rule`)** | No Access | No Access | Read Only | Full CRUD |
| **Billing Logs (`brightloop.billing.log`)** | No Access | No Access | Read Only | Full CRUD |
| **Internal Staff User Management (`res.users`)** | **No Access** | **No Access** | **Strictly Forbidden** | **Full CRUD** |
| **System Settings (`res.config.settings`)** | No Access | No Access | No Access | Full CRUD |

---

## 3. Record-Level Security Rules (ir.rule)

### 3.1 Customer Subscription Isolation Rule
- **Model:** `brightloop.subscription`
- **Rule ID:** `brightloop_subscription_rule_portal`
- **Target Group:** `brightloop_base.group_brightloop_portal`
- **Permitted Operations:** Read Only (`perm_read=1`, `perm_write=0`, `perm_create=0`, `perm_unlink=0`)
- **Domain Force:**
  ```python
  ['|', ('partner_id', '=', user.partner_id.id), ('partner_id', 'child_of', user.partner_id.commercial_partner_id.id)]
  ```
- **Guaranteed Effect:** Even if an RPC call requests all subscriptions (`search([])`), the PostgreSQL query automatically appends:
  ```sql
  WHERE partner_id = <current_user_partner_id>
  ```
  preventing any cross-customer record leakage.

### 3.2 Customer Invoice Isolation Rule
- **Model:** `account.move`
- **Target Group:** `brightloop_base.group_brightloop_portal`
- **Domain Force:**
  ```python
  ['&', ('move_type', '=', 'out_invoice'), '|', ('partner_id', '=', user.partner_id.id), ('partner_id', 'child_of', user.partner_id.commercial_partner_id.id)]
  ```

---

## 4. Administrative Staff Protection Rule

### Server-Side Staff Creation Barrier (`models/res_users.py`)
- **Problem Solved:** An internal staff user cannot invite or promote another user to `group_brightloop_user` or `group_brightloop_admin`.
- **Enforcement Mechanism:**
  - Hooked on `res.users.create` and `res.users.write`.
  - Condition: If `group_ids` contains `group_brightloop_user` or `group_brightloop_admin`, verify `self.env.user.has_group('brightloop_base.group_brightloop_admin')`.
  - Violations raise:
    ```python
    AccessError(_("Access Denied: Only Brightloop Administrators can assign internal staff or administrator roles."))
    ```
