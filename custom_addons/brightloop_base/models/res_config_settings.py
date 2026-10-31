# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    brightloop_auto_close_days = fields.Integer(
        string="Auto-Close Grace Period (Days)",
        default=15,
        config_parameter='brightloop.auto_close_days',
        help="Number of days after subscription expiry or overdue payment before an active subscription is automatically closed."
    )
    brightloop_invoice_auto_send = fields.Boolean(
        string="Auto-Send Invoices by Email",
        default=True,
        config_parameter='brightloop.invoice_auto_send',
        help="When enabled, recurring invoices generated on billing day will be automatically emailed to the customer."
    )
    brightloop_allow_daily_billing = fields.Boolean(
        string="Enable Daily Billing Frequencies",
        default=True,
        config_parameter='brightloop.allow_daily_billing',
        help="Allows subscription plans to be configured with daily billing intervals."
    )

