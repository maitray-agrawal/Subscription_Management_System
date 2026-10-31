# Database Models and Relationships
## Brightloop Subscription Management System

### Summary of Models

| Technical Model | Type | Module | Core Functionality |
|---|---|---|---|
| `brightloop.subscription.plan` | Custom | `brightloop_subscription` | Recurrence rules, availability windows, operational flags |
| `brightloop.subscription` | Custom | `brightloop_subscription` | Central contract entity, lifecycle state machine |
| `brightloop.subscription.line` | Custom | `brightloop_subscription` | Contract line items with product, qty, pricing, taxes |
| `brightloop.quotation.template` | Custom | `brightloop_subscription` | Preset quotation header definitions |
| `brightloop.quotation.template.line` | Custom | `brightloop_subscription` | Preset quotation line items |
| `brightloop.billing.log` | Custom | `brightloop_billing` | Billing run tracking, audit trail, retry counter |
| `brightloop.discount.rule` | Custom | `brightloop_discount` | Discount definition and eligibility constraints |
| `brightloop.discount.usage` | Custom | `brightloop_discount` | Tracking log of applied discount instances |
| `res.partner` | Native Extension | Base / Odoo | Customer identity, commercial entity |
| `product.template` | Native Extension | `brightloop_subscription` | Catalog products with subscription flags |
| `product.product` | Native Extension | `brightloop_subscription` | Specific product variants with price extras |
| `account.move` | Native Extension | `brightloop_billing` | Invoices linked to subscriptions via `subscription_id` |
| `account.payment` | Native Reused | Account | Reconciled payments |

---

### Detailed Model Specifications

#### 1. `brightloop.subscription.plan`
- **Fields**:
  - `name` (Char, required, indexed)
  - `code` (Char)
  - `billing_unit` (Selection: `day`, `week`, `month`, `year`, default=`month`, required)
  - `billing_interval` (Integer, default=1, required)
  - `min_quantity` (Float, default=1.0)
  - `date_start` (Date)
  - `date_end` (Date)
  - `auto_close_on_expiry` (Boolean, default=True)
  - `allow_early_closure` (Boolean, default=True)
  - `allow_pause` (Boolean, default=True)
  - `allow_renewal` (Boolean, default=True)
  - `payment_term_id` (Many2one `account.payment.term`)
  - `active` (Boolean, default=True)
- **Constraints**:
  - `CHECK(billing_interval > 0)`: Billing interval must be strictly positive.
  - `CHECK(min_quantity >= 0)`: Minimum quantity cannot be negative.
  - Date validity constraint: `date_end` >= `date_start`.

#### 2. `brightloop.subscription`
- **Fields**:
  - `name` (Char, readonly, default='New', copy=False, sequence)
  - `partner_id` (Many2one `res.partner`, required, index=True)
  - `plan_id` (Many2one `brightloop.subscription.plan`, required, index=True)
  - `state` (Selection: `draft`, `quotation`, `confirmed`, `active`, `closed`, default=`draft`, tracking=True, index=True)
  - `is_paused` (Boolean, default=False, tracking=True)
  - `pause_date` (Date, readonly=True)
  - `start_date` (Date, default=fields.Date.context_today, required)
  - `expiry_date` (Date, tracking=True)
  - `next_billing_date` (Date, index=True, copy=False)
  - `last_billing_date` (Date, copy=False)
  - `payment_term_id` (Many2one `account.payment.term`)
  - `line_ids` (One2many `brightloop.subscription.line`, 'subscription_id')
  - `invoice_ids` (One2many `account.move`, 'subscription_id')
  - `discount_rule_ids` (Many2many `brightloop.discount.rule`)
  - `billing_log_ids` (One2many `brightloop.billing.log`, 'subscription_id')
  - `currency_id` (Many2one `res.currency`, default=company currency)
  - `amount_untaxed` (Monetary, compute='_compute_amounts', store=True)
  - `amount_tax` (Monetary, compute='_compute_amounts', store=True)
  - `amount_total` (Monetary, compute='_compute_amounts', store=True)
  - `mrr` (Monetary, compute='_compute_mrr', store=True)
- **Business Methods**:
  - `action_to_quotation()`: Moves state from `draft` to `quotation`.
  - `action_confirm()`: Moves state from `quotation` to `confirmed`.
  - `action_activate()`: Moves state from `confirmed` to `active`, computes initial `next_billing_date`.
  - `action_pause()`: Sets `is_paused=True` (if plan permits).
  - `action_resume()`: Sets `is_paused=False`, recalculates next billing date if paused for extended time.
  - `action_close()`: Moves state to `closed` (verifies early closure permission if before expiry).
  - `action_renew()`: Creates a new renewal subscription or extends period (if plan permits).
  - `action_generate_invoice()`: Idempotently creates an invoice for the current period.

#### 3. `brightloop.subscription.line`
- **Fields**:
  - `subscription_id` (Many2one `brightloop.subscription`, required, ondelete='cascade', index=True)
  - `product_id` (Many2one `product.product`, required)
  - `name` (Text, required)
  - `quantity` (Float, default=1.0, required)
  - `price_unit` (Float, required)
  - `tax_ids` (Many2many `account.tax`)
  - `discount` (Float, default=0.0)
  - `price_subtotal` (Monetary, compute='_compute_amounts', store=True)
  - `price_total` (Monetary, compute='_compute_amounts', store=True)
  - `currency_id` (Many2one `res.currency`, related='subscription_id.currency_id')

#### 4. `brightloop.billing.log`
- **Fields**:
  - `subscription_id` (Many2one `brightloop.subscription`, required, index=True)
  - `invoice_id` (Many2one `account.move`, index=True)
  - `execution_date` (Datetime, default=fields.Datetime.now, required)
  - `period_start` (Date, required)
  - `period_end` (Date, required)
  - `status` (Selection: `success`, `failed`, `skipped`, required)
  - `message` (Text)
  - `retry_count` (Integer, default=0)

#### 5. `brightloop.discount.rule`
- **Fields**:
  - `name` (Char, required)
  - `code` (Char, index=True)
  - `discount_type` (Selection: `fixed`, `percent`, required, default=`percent`)
  - `discount_value` (Float, required)
  - `min_purchase_amount` (Monetary, default=0.0)
  - `min_quantity` (Float, default=0.0)
  - `date_start` (Date)
  - `date_end` (Date)
  - `usage_limit` (Integer, default=0, help="0 indicates unlimited")
  - `current_usage_count` (Integer, default=0, readonly=True)
  - `scope` (Selection: `subscription`, `specific_products`, required, default=`subscription`)
  - `product_ids` (Many2many `product.product`)
  - `active` (Boolean, default=True)

#### 6. `brightloop.discount.usage`
- **Fields**:
  - `discount_rule_id` (Many2one `brightloop.discount.rule`, required, index=True)
  - `subscription_id` (Many2one `brightloop.subscription`, required, index=True)
  - `invoice_id` (Many2one `account.move`, required, index=True)
  - `discount_amount` (Monetary, required)
  - `applied_date` (Datetime, default=fields.Datetime.now)
