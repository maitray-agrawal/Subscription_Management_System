# Brightloop Subscription Management System — Requirement Traceability Matrix

## Document Overview
- **Document Version:** 1.0.0
- **Status:** Approved Baseline / Active
- **Module Ownership:** `brightloop_subscription`, `brightloop_base`, `brightloop_portal`, `brightloop_billing`
- **Target ERP Platform:** Odoo 19 (Community/Enterprise)

---

## 1. Role Definitions & Security Context

| Role Code | Role Name | System Group / Access Context | Scope of Responsibility |
|---|---|---|---|
| **CUST** | Customer | `base.group_portal` | Self-service subscription viewing, quotation approval, cancellation requests, portal profile management. |
| **EVAL** | Evaluator | `brightloop_portal.group_evaluator` | Read-only sandbox evaluator access to mock plans, quotation previews, and guided walkthroughs. |
| **STAF** | Subscription Staff / User | `brightloop_subscription.group_subscription_user` | Creates quotations, registers customers, assists with manual renewals, configures customer subscriptions. |
| **MGR** | Subscription Manager | `brightloop_subscription.group_subscription_manager` | Full administrative control: creates plans, quotation templates, triggers overrides, approves early closures, manages billing frequencies. |

---

## 2. Requirement Traceability Matrix

### 2.1 Customer Registration & Role Management

| Req ID | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|
| **REQ-SUB-001** | Public visitors must be able to register for a subscription account via the portal by submitting name, valid email, company (optional), and password. | CUST | System creates a new `res.partner` record marked as a subscription customer and sends a welcome/verification email with an activation token. | `brightloop_portal`, `brightloop_base` | 1. Duplicate email addresses are rejected with a clear validation error.<br>2. Account is assigned to `base.group_portal`.<br>3. `is_subscription_customer` flag is set to `True` on the partner record. |
| **REQ-SUB-002** | Subscription Staff must be able to create customer profiles manually from the backend with mandatory contact and billing metadata. | STAF, MGR | Customer record is persisted in `res.partner` with default payment terms, tax position, and currency. | `brightloop_base` | 1. Mandatory fields: Name, Email, Country, Currency.<br>2. Staff cannot assign administrative privileges to customer records. |
| **REQ-SUB-003** | Evaluator accounts must have access restricted exclusively to demo subscription plans and read-only views of quotation templates. | EVAL | System prevents evaluator from generating live invoices, modifying customer records, or activating commercial subscriptions. | `brightloop_portal`, `brightloop_subscription` | 1. Evaluator cannot transition quotations to `Active`.<br>2. Backend admin menus remain hidden from evaluator users. |
| **REQ-SUB-004** | Role-based permission controls must enforce strict separation of duties between Subscription Staff and Subscription Managers. | STAF, MGR | Subscription Staff can create and edit Draft subscriptions but cannot delete confirmed/active records or alter system-wide subscription plans without Manager role. | `brightloop_subscription` | 1. Delete button hidden for non-managers on non-draft records.<br>2. Plan creation/editing restricted to `group_subscription_manager`. |

---

### 2.2 Products & Product Variants

| Req ID | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|
| **REQ-SUB-005** | Products must support a "Can be Subscribed" flag to distinguish recurring services from one-off consumables/storable goods. | MGR | Odoo `product.template` exposes `recurring_invoice = True` and displays recurring configuration tabs only when enabled. | `brightloop_subscription` | 1. Products without the flag cannot be selected on subscription plan lines.<br>2. Default product type is set to `service`. |
| **REQ-SUB-006** | Subscription products must support multi-dimensional attribute variants (e.g., Tier: Basic/Pro/Enterprise; Seats: 1-5/6-20/20+; Support: Standard/24-7). | MGR, STAF | System automatically generates `product.product` variant records with distinct extra prices and attribute value linkages. | `brightloop_subscription` | 1. Selecting variant attributes on quotation line updates unit price dynamically based on attribute price surcharges.<br>2. Stock delivery logic is suppressed for service-based recurring variants. |
| **REQ-SUB-007** | Product variants must allow independent price overrides per subscription plan and currency without altering base catalog prices. | MGR | System calculates variant line prices using subscription plan price matrices or standard price-list rules. | `brightloop_subscription` | 1. Plan-specific price overrides take precedence over standard variant list price.<br>2. Zero or negative prices are prevented unless explicitly configured as a 100% discount promotional line. |

---

### 2.3 Subscription Plans & Pricing Models

| Req ID | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|
| **REQ-SUB-008** | Subscription plans must define standard recurrence parameters including billing period (Daily, Weekly, Monthly, Quarterly, Semi-Annual, Annual). | MGR | Plan configuration stores recurrence interval (`billing_interval_number`, `billing_interval_unit`). | `brightloop_subscription` | 1. Valid units: `day`, `week`, `month`, `year`.<br>2. Interval number must be a positive integer ($\ge 1$).<br>3. Custom combinations like "every 3 months" (Quarterly) are natively supported. |
| **REQ-SUB-009** | Subscription plans must specify contract commitment duration (e.g., 12-month fixed term, rolling month-to-month, indefinite). | MGR, STAF | System tracks contract start date, commitment end date, and auto-renewal eligibility. | `brightloop_subscription` | 1. If commitment term is defined, early cancellation triggers penalty or commitment warning.<br>2. Indefinite contracts remain active until explicit termination. |
| **REQ-SUB-010** | Subscription plans must support auto-close rules triggered by prolonged non-payment or overdue invoice thresholds. | MGR | System automatically marks an active subscription as `Closed` if unpaid invoices exceed configured grace period (default: 15 days). | `brightloop_subscription`, `brightloop_billing` | 1. Grace period configurable per plan (days).<br>2. Automated cron job evaluates overdue days and executes cancellation transition.<br>3. Activity log / chatter logs reason for auto-closure. |

---

### 2.4 Billing Frequency & Minimum Quantity Scenarios

| Req ID | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|
| **REQ-SUB-011** | System must enforce a configurable minimum order quantity (MOQ) per subscription plan or product line. | STAF, CUST | If quantity entered is below the minimum threshold (e.g., min 5 user seats for Enterprise Plan), system blocks confirmation and alerts user. | `brightloop_subscription` | 1. Validation error thrown if `line.quantity < product.min_subscription_qty`.<br>2. Portal orders automatically adjust or block submission below MOQ. |
| **REQ-SUB-012** | Subscription billing frequency must validate alignment between plan interval and invoice generation schedule. | MGR, STAF | Recurring invoice generation cron calculates `next_invoice_date` strictly in accordance with plan billing interval. | `brightloop_subscription`, `brightloop_billing` | 1. For monthly plans, date rolls over to identical day of next month (handling month-end clipping, e.g. Jan 31 -> Feb 28).<br>2. Leap year Feb 29 rollover correctly targets Feb 28 in non-leap subsequent years. |
| **REQ-SUB-013** | Prorated billing must be supported for mid-cycle activations or mid-cycle seat additions. | MGR, STAF | Invoicing engine computes fractional interval charge based on remaining days in the active billing cycle. | `brightloop_subscription`, `brightloop_billing` | 1. Formula: $\text{Prorated Amount} = \text{Unit Price} \times \text{Quantity} \times \left(\frac{\text{Days Remaining}}{\text{Total Days in Period}}\right)$.<br>2. Prorated invoice line is clearly labeled with date range. |

---

### 2.5 Quotation Templates & Quotation Generation

| Req ID | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|
| **REQ-SUB-014** | Staff must be able to generate subscription quotations using pre-configured Quotation Templates containing standard lines, terms, and default plans. | STAF | System populates subscription order lines, plan duration, terms & conditions, and default add-ons from the chosen template. | `brightloop_subscription` | 1. Applying a template does not overwrite existing custom partner details.<br>2. Staff can override line quantities and add optional products. |
| **REQ-SUB-015** | Quotations must have a configurable expiration date (`validity_date`) after which customer acceptance via portal is locked. | STAF, CUST | Expired quotations display "Expired" status in portal and reject online signing/confirmation. | `brightloop_subscription`, `brightloop_portal` | 1. Expiration defaults to template validity window (e.g., 30 days).<br>2. Staff can manually extend quotation validity. |
| **REQ-SUB-016** | Customer must be able to review, accept, electronically sign, and pay the initial quotation online through the customer portal. | CUST | Online confirmation triggers transition from `Quotation` to `Confirmed`, records digital signature with timestamp, and initiates payment transaction. | `brightloop_portal`, `brightloop_subscription` | 1. PDF quotation summary generated with signature audit trail.<br>2. Chatter logs electronic signature IP address and timestamp. |

---

### 2.6 Subscription Lifecycle: Transitions & Scenarios

| Req ID | Exact Expected Behaviour | User Role | Expected System Result | Relevant Module | Acceptance Criteria |
|---|---|---|---|---|---|
| **REQ-SUB-017** | Subscriptions must follow strict lifecycle states: `Draft` $\rightarrow$ `Quotation` $\rightarrow$ `Confirmed` $\rightarrow$ `Active` $\rightarrow$ `Closed`. | STAF, MGR, CUST | State transitions follow validated paths; direct jumps across unconfirmed states are rejected. | `brightloop_subscription` | 1. Transition rules strictly enforced at database and ORM level.<br>2. Status bar updates dynamically on form views. |
| **REQ-SUB-018** | Transition from `Draft` to `Quotation` must require customer assignment, valid plan, and at least one subscription line with quantity $> 0$. | STAF | Subscription enters `Quotation` state and quotation reference/number is generated. | `brightloop_subscription` | 1. Validation fails if lines are empty or total is zero.<br>2. PDF quote becomes downloadable. |
| **REQ-SUB-019** | Transition from `Confirmed` to `Active` must occur upon receipt of first payment confirmation or explicit staff authorization. | STAF, MGR | Subscription state becomes `Active`; recurring invoicing cron schedule is activated; `date_start` is set. | `brightloop_subscription`, `brightloop_billing` | 1. Invoicing schedule initialized (`next_invoice_date = date_start` or `date_start + 1 interval` depending on prepaid/postpaid config).<br>2. Access rights/entitlements provisioning hook triggered. |
| **REQ-SUB-020** | Active subscriptions must support temporary "Pause" status with frozen billing for a defined suspension window. | MGR, STAF | Subscription enters paused mode (`is_paused = True`); automated recurring invoicing skips paused periods; service entitlement paused. | `brightloop_subscription` | 1. Reason for pause must be recorded.<br>2. Resuming subscription recalculates `next_invoice_date` to adjust for paused duration.<br>3. Maximum pause duration enforced per plan policy. |
| **REQ-SUB-021** | Subscriptions with auto-renew enabled must automatically renew upon reaching commitment end date. | SYSTEM (Cron) | System generates renewal quotation or extends commitment end date by renewal interval and triggers next cycle invoice. | `brightloop_subscription`, `brightloop_billing` | 1. Notification email sent to customer 15 days prior to auto-renewal.<br>2. If auto-renew is `False`, subscription enters expiration pending state. |
| **REQ-SUB-022** | Early closure requested by customer or staff must enforce early termination terms, calculate penalty if applicable, and transition state to `Closed`. | MGR | Subscription transitions to `Closed`; `close_reason_id` and `date_closed` recorded; pending unbilled usage invoiced. | `brightloop_subscription` | 1. Mandatory closure reason selection from predefined master list.<br>2. Inactive recurring cron ceases future invoice generation.<br>3. Early termination fee line added if before commitment end date. |
| **REQ-SUB-023** | Subscriptions with unpaid invoices beyond grace period must be automatically closed by system maintenance cron. | SYSTEM (Cron) | Subscription transitions to `Closed` with reason "Automatic Closure: Non-Payment"; notification dispatched to customer and account manager. | `brightloop_subscription`, `brightloop_billing` | 1. Audit log recorded in chatter.<br>2. Associated portal customer account flagged for restricted access. |
