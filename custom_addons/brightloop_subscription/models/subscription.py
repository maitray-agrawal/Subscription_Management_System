# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BrightloopSubscription(models.Model):
    _name = 'brightloop.subscription'
    _description = 'Subscription Record'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    name = fields.Char(
        string="Subscription Number",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True,
        index=True,
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    plan_id = fields.Many2one(
        'brightloop.subscription.plan',
        string="Subscription Plan",
        required=True,
        index=True,
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    template_id = fields.Many2one(
        'brightloop.quotation.template',
        string="Quotation Template",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('quotation', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], string="Status", default='draft', required=True, tracking=True, index=True)

    # Operational flags
    is_paused = fields.Boolean(
        string="Is Paused",
        default=False,
        tracking=True,
        copy=False,
        help="Flag indicating if recurring billing and services are temporarily suspended."
    )
    pause_date = fields.Date(string="Paused On", readonly=True, copy=False)
    close_reason = fields.Char(string="Close Reason", copy=False, tracking=True)

    # Contract Dates
    start_date = fields.Date(
        string="Start Date",
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    expiry_date = fields.Date(
        string="End Date / Expiry",
        tracking=True,
        help="Date when the subscription contract ends."
    )
    validity_date = fields.Date(
        string="Quotation Valid Until",
        copy=False,
        help="Date after which this quotation can no longer be accepted by the customer."
    )
    next_billing_date = fields.Date(
        string="Next Billing Date",
        copy=False,
        tracking=True,
        index=True,
        help="Billing date pointer used by recurring invoice generation."
    )
    last_billing_date = fields.Date(
        string="Last Invoiced Date",
        copy=False,
        readonly=True
    )

    # Commercial & Accounting terms
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Payment Terms",
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        compute='_compute_currency_id',
        store=True,
        readonly=False
    )

    origin_subscription_id = fields.Many2one(
        'brightloop.subscription',
        string="Renewed From",
        readonly=True,
        copy=False,
        index=True
    )
    renewal_subscription_ids = fields.One2many(
        'brightloop.subscription',
        'origin_subscription_id',
        string="Renewal Subscriptions"
    )

    line_ids = fields.One2many(
        'brightloop.subscription.line',
        'subscription_id',
        string="Subscription Lines",
        copy=True
    )

    # Financial Totals
    amount_untaxed = fields.Monetary(string="Untaxed Amount", compute='_compute_amounts', store=True, tracking=True)
    amount_tax = fields.Monetary(string="Taxes", compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string="Total Amount", compute='_compute_amounts', store=True, tracking=True)
    total_quantity = fields.Float(string="Total Quantity", compute='_compute_amounts', store=True)

    mrr = fields.Monetary(
        string="Monthly Recurring Revenue (MRR)",
        compute='_compute_mrr',
        store=True,
        tracking=True,
        help="Normalized monthly recurring revenue based on plan recurrence."
    )

    # Stage 4 Billing Interface Contract
    is_eligible_for_billing = fields.Boolean(
        string="Eligible for Invoicing",
        compute='_compute_billing_eligibility',
        index=True,
        store=True,
        help="True when subscription is Active, not Paused, and due for billing."
    )
    invoice_count = fields.Integer(string="Invoices Count", compute='_compute_invoice_count')

    @api.depends('company_id')
    def _compute_currency_id(self):
        for sub in self:
            sub.currency_id = sub.company_id.currency_id

    @api.depends('line_ids.price_subtotal', 'line_ids.price_total', 'line_ids.quantity')
    def _compute_amounts(self):
        for sub in self:
            sub.amount_untaxed = sum(sub.line_ids.mapped('price_subtotal'))
            sub.amount_tax = sum(sub.line_ids.mapped('price_total')) - sub.amount_untaxed
            sub.amount_total = sum(sub.line_ids.mapped('price_total'))
            sub.total_quantity = sum(sub.line_ids.mapped('quantity'))

    @api.depends('amount_untaxed', 'plan_id.billing_unit', 'plan_id.billing_interval')
    def _compute_mrr(self):
        for sub in self:
            if not sub.plan_id or not sub.amount_untaxed:
                sub.mrr = 0.0
                continue
            interval = sub.plan_id.billing_interval or 1
            unit = sub.plan_id.billing_unit
            if unit == 'month':
                sub.mrr = sub.amount_untaxed / interval
            elif unit == 'year':
                sub.mrr = sub.amount_untaxed / (12 * interval)
            elif unit == 'week':
                sub.mrr = (sub.amount_untaxed * 52) / (12 * interval)
            elif unit == 'day':
                sub.mrr = (sub.amount_untaxed * 30) / interval
            else:
                sub.mrr = sub.amount_untaxed

    @api.depends('state', 'is_paused', 'next_billing_date')
    def _compute_billing_eligibility(self):
        today = fields.Date.context_today(self)
        for sub in self:
            sub.is_eligible_for_billing = (
                sub.state == 'active' and
                not sub.is_paused and
                bool(sub.next_billing_date and sub.next_billing_date <= today)
            )

    def _compute_invoice_count(self):
        # Stub for Stage 4 integration: reads account.move where subscription_id = sub.id
        move_model = self.env['account.move']
        if 'subscription_id' in move_model._fields:
            move_data = move_model._read_group(
                [('subscription_id', 'in', self.ids)],
                ['subscription_id'],
                ['__count']
            )
            counts = {sub.id: count for sub, count in move_data}
            for sub in self:
                sub.invoice_count = counts.get(sub.id, 0)
        else:
            for sub in self:
                sub.invoice_count = 0

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.plan_id = self.template_id.plan_id
            if self.template_id.validity_days:
                self.validity_date = fields.Date.context_today(self) + relativedelta(days=self.template_id.validity_days)
            # Populate lines from template
            lines = []
            for t_line in self.template_id.line_ids:
                lines.append((0, 0, {
                    'product_id': t_line.product_id.id,
                    'name': t_line.name,
                    'quantity': t_line.quantity,
                    'price_unit': t_line.price_unit,
                    'tax_ids': [(6, 0, t_line.product_id.taxes_id.ids)],
                }))
            if lines:
                self.line_ids = lines

    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        if self.plan_id and self.plan_id.payment_term_id and not self.payment_term_id:
            self.payment_term_id = self.plan_id.payment_term_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('template_id'):
                template = self.env['brightloop.quotation.template'].browse(vals['template_id'])
                if template.exists():
                    if not vals.get('plan_id') and template.plan_id:
                        vals['plan_id'] = template.plan_id.id
                    if not vals.get('validity_date') and template.validity_days:
                        vals['validity_date'] = fields.Date.context_today(self) + relativedelta(days=template.validity_days)
                    if not vals.get('line_ids') and template.line_ids:
                        vals['line_ids'] = [(0, 0, {
                            'product_id': t_line.product_id.id,
                            'name': t_line.name,
                            'quantity': t_line.quantity,
                            'price_unit': t_line.price_unit,
                            'tax_ids': [(6, 0, t_line.product_id.taxes_id.ids)],
                        }) for t_line in template.line_ids]
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # STATE MACHINE WORKFLOWS & CONSTRAINTS
    # -------------------------------------------------------------------------

    def action_to_quotation(self):
        """Moves a Draft subscription to Quotation, performing validation."""
        for sub in self:
            if sub.state != 'draft':
                raise ValidationError(_("Only Draft subscriptions can be transitioned to Quotation."))

            if not sub.line_ids:
                raise ValidationError(_("A subscription must contain at least one product line before creating a quotation."))

            # Verify plan availability window
            today = fields.Date.context_today(self)
            if not sub.plan_id.is_available_on(today):
                raise ValidationError(_(
                    "The plan '%s' is not available for quoting on %s.",
                    sub.plan_id.name, today
                ))

            # Verify minimum quantity constraint
            if sub.total_quantity < sub.plan_id.min_quantity:
                raise ValidationError(_(
                    "The total quantity (%s) is less than the plan minimum required quantity (%s) for '%s'.",
                    sub.total_quantity, sub.plan_id.min_quantity, sub.plan_id.name
                ))

            # Assign sequence if New
            if sub.name == _('New'):
                sub.name = self.env['ir.sequence'].next_by_code('brightloop.subscription') or _('New')

            sub.write({'state': 'quotation'})
            sub.message_post(body=_("Quotation '%s' created from draft.", sub.name))

    def action_confirm(self):
        """Transitions a Quotation to Confirmed state."""
        for sub in self:
            if sub.state != 'quotation':
                raise ValidationError(_("Only Quotations can be confirmed."))

            # Enforce minimum quantity constraint check again
            if sub.total_quantity < sub.plan_id.min_quantity:
                raise ValidationError(_(
                    "Cannot confirm: Total quantity (%s) is below plan minimum (%s).",
                    sub.total_quantity, sub.plan_id.min_quantity
                ))

            sub.write({'state': 'confirmed'})
            sub.message_post(body=_("Subscription confirmed by customer or sales representative."))

    def action_activate(self):
        """Activates a Confirmed subscription and initializes billing schedule."""
        for sub in self:
            if sub.state != 'confirmed':
                raise ValidationError(_("Only Confirmed subscriptions can be activated."))

            start = sub.start_date or fields.Date.context_today(self)
            # Schedule initial next billing date
            next_bill = sub.plan_id.calculate_next_billing_date(start)

            sub.write({
                'state': 'active',
                'start_date': start,
                'next_billing_date': next_bill,
            })
            sub.message_post(body=_(
                "Subscription activated. Contract start date: %s. First scheduled billing date: %s.",
                start, next_bill
            ))

    def action_pause(self):
        """Temporarily pauses an Active subscription if allowed by plan."""
        for sub in self:
            if sub.state != 'active':
                raise UserError(_("Only Active subscriptions can be paused."))
            if sub.is_paused:
                raise UserError(_("Subscription is already paused."))
            if not sub.plan_id.allow_pause:
                raise UserError(_("Plan '%s' does not permit pausing subscriptions.", sub.plan_id.name))

            sub.write({
                'is_paused': True,
                'pause_date': fields.Date.context_today(self)
            })
            sub.message_post(body=_("Subscription has been paused. Invoicing is suspended."))

    def action_resume(self):
        """Resumes a paused Active subscription."""
        for sub in self:
            if sub.state != 'active' or not sub.is_paused:
                raise UserError(_("Only paused active subscriptions can be resumed."))

            sub.write({
                'is_paused': False,
                'pause_date': False
            })
            sub.message_post(body=_("Subscription resumed. Recurring services and invoicing are active."))

    def action_close(self, reason=None):
        """Closes a subscription, verifying early closure permissions if before expiry."""
        today = fields.Date.context_today(self)
        for sub in self:
            if sub.state == 'closed':
                raise UserError(_("Subscription is already closed."))

            # Check if this is an early closure before expiry
            if sub.expiry_date and today < sub.expiry_date:
                if not sub.plan_id.allow_early_closure:
                    raise UserError(_("Plan '%s' does not permit early closure before expiration.", sub.plan_id.name))

            vals = {
                'state': 'closed',
                'is_paused': False,
                'next_billing_date': False,
            }
            if reason:
                vals['close_reason'] = reason
            sub.write(vals)
            sub.message_post(body=_("Subscription closed. Reason: %s", reason or _("Not specified")))

    def action_renew(self):
        """Creates a renewal subscription contract or extends term if permitted."""
        self.ensure_one()
        if not self.plan_id.allow_renewal:
            raise UserError(_("Plan '%s' does not permit renewals.", self.plan_id.name))

        # Create new subscription linked to current
        renewal_vals = {
            'partner_id': self.partner_id.id,
            'plan_id': self.plan_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'payment_term_id': self.payment_term_id.id if self.payment_term_id else False,
            'origin_subscription_id': self.id,
            'state': 'draft',
            'start_date': self.expiry_date or fields.Date.context_today(self),
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }) for line in self.line_ids],
        }
        renewal_sub = self.create(renewal_vals)
        self.message_post(body=_("Renewal subscription created: <a href='#' data-oe-model='brightloop.subscription' data-oe-id='%s'>%s</a>", renewal_sub.id, renewal_sub.name))
        return {
            'name': _('Renewal Subscription'),
            'type': 'ir.actions.act_window',
            'res_model': 'brightloop.subscription',
            'res_id': renewal_sub.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def cron_auto_close_expired(self):
        """Scheduled action to auto-close subscriptions that reached their expiry date."""
        today = fields.Date.context_today(self)
        expired_subs = self.search([
            ('state', '=', 'active'),
            ('expiry_date', '!=', False),
            ('expiry_date', '<', today),
            ('plan_id.auto_close_on_expiry', '=', True)
        ])
        for sub in expired_subs:
            sub.action_close(reason=_("Automatic closure: Subscription reached contract end date."))


class BrightloopSubscriptionLine(models.Model):
    _name = 'brightloop.subscription.line'
    _description = 'Subscription Item Line'
    _order = 'id'

    subscription_id = fields.Many2one(
        'brightloop.subscription',
        string="Subscription",
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True,
        domain="[('sale_ok', '=', True)]"
    )
    name = fields.Text(string="Description", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    price_unit = fields.Float(string="Unit Price", required=True, default=0.0)
    tax_ids = fields.Many2many(
        'account.tax',
        string="Taxes",
        domain="[('type_tax_use', '=', 'sale')]"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='subscription_id.currency_id',
        store=True
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amounts',
        store=True
    )
    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amounts',
        store=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            # In Odoo, product.product.lst_price natively resolves Base Price + Price Extras (e.g. Odoo brand +560)
            self.price_unit = self.product_id.lst_price
            if self.product_id.taxes_id:
                self.tax_ids = [(6, 0, self.product_id.taxes_id.ids)]

    @api.depends('quantity', 'price_unit', 'tax_ids')
    def _compute_amounts(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            line.price_subtotal = subtotal
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(
                    line.price_unit,
                    currency=line.currency_id,
                    quantity=line.quantity,
                    product=line.product_id,
                    partner=line.subscription_id.partner_id
                )
                line.price_total = taxes['total_included']
            else:
                line.price_total = subtotal
