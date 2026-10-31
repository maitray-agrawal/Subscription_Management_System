# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BrightloopSubscriptionPlan(models.Model):
    _name = 'brightloop.subscription.plan'
    _description = 'Subscription Plan'
    _order = 'sequence, name'

    name = fields.Char(string="Plan Name", required=True, translate=True, index='trigram')
    code = fields.Char(string="Code", index=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Billing Frequency / Recurrence
    billing_unit = fields.Selection([
        ('day', 'Daily'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ], string="Billing Frequency", required=True, default='month')
    billing_interval = fields.Integer(string="Interval Number", required=True, default=1)
    billing_frequency_display = fields.Char(
        string="Billing Terms",
        compute='_compute_billing_frequency_display',
        store=True
    )

    # Minimum Quantity Enforcement
    min_quantity = fields.Float(
        string="Minimum Quantity",
        required=True,
        default=1.0,
        help="Minimum required order quantity for subscriptions created under this plan."
    )

    # Plan Availability Dates
    date_start = fields.Date(string="Available From", help="First date this plan can be offered to customers.")
    date_end = fields.Date(string="Available Until", help="Last date this plan can be offered.")

    # Operational & Lifecycle Permissions
    auto_close_on_expiry = fields.Boolean(
        string="Auto-Close on Expiry",
        default=True,
        help="If checked, subscriptions under this plan will automatically transition to Closed upon reaching their expiry date."
    )
    allow_early_closure = fields.Boolean(
        string="Allow Early Closure",
        default=True,
        help="Permits customers and operational staff to terminate subscriptions before the end date."
    )
    allow_pause = fields.Boolean(
        string="Allow Pause & Resume",
        default=True,
        help="Allows temporarily suspending an active subscription and pausing recurring billing."
    )
    allow_renewal = fields.Boolean(
        string="Allow Renewal",
        default=True,
        help="Permits renewing expired or active contracts for subsequent terms."
    )

    # Default Payment Terms
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Default Payment Terms"
    )

    # Statistics / Counting
    subscription_count = fields.Integer(
        string="Subscriptions",
        compute='_compute_subscription_count'
    )

    _check_billing_interval = models.Constraint(
        'CHECK(billing_interval > 0)',
        'The billing interval must be strictly positive.'
    )
    _check_min_quantity = models.Constraint(
        'CHECK(min_quantity >= 0)',
        'The minimum quantity cannot be negative.'
    )

    @api.constrains('date_start', 'date_end')
    def _check_availability_dates(self):
        for plan in self:
            if plan.date_start and plan.date_end and plan.date_end < plan.date_start:
                raise ValidationError(_("The availability end date cannot be earlier than the start date."))

    @api.depends('billing_unit', 'billing_interval')
    def _compute_billing_frequency_display(self):
        for plan in self:
            val = plan.billing_interval
            unit_map = {
                'day': ('Day', 'Days'),
                'week': ('Week', 'Weeks'),
                'month': ('Month', 'Months'),
                'year': ('Year', 'Years'),
            }
            singular, plural = unit_map.get(plan.billing_unit, ('Period', 'Periods'))
            if val == 1:
                plan.billing_frequency_display = _("Every %s", singular)
            else:
                plan.billing_frequency_display = _("Every %s %s", val, plural)

    def _compute_subscription_count(self):
        sub_data = self.env['brightloop.subscription']._read_group(
            [('plan_id', 'in', self.ids)],
            ['plan_id'],
            ['__count']
        )
        counts = {plan.id: count for plan, count in sub_data}
        for plan in self:
            plan.subscription_count = counts.get(plan.id, 0)

    def calculate_next_billing_date(self, from_date):
        """Calculates the subsequent billing date based on this plan's recurrence."""
        self.ensure_one()
        if not from_date:
            from_date = fields.Date.context_today(self)

        interval = self.billing_interval
        unit = self.billing_unit

        if unit == 'day':
            return from_date + relativedelta(days=interval)
        elif unit == 'week':
            return from_date + relativedelta(weeks=interval)
        elif unit == 'month':
            return from_date + relativedelta(months=interval)
        elif unit == 'year':
            return from_date + relativedelta(years=interval)
        return from_date

    def is_available_on(self, check_date=None):
        """Validates if the plan is currently available for quoting on a specific date."""
        self.ensure_one()
        if not check_date:
            check_date = fields.Date.context_today(self)
        if self.date_start and check_date < self.date_start:
            return False
        if self.date_end and check_date > self.date_end:
            return False
        return True
