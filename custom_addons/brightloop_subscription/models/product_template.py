# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription_product = fields.Boolean(
        string="Can be Subscribed",
        default=False,
        help="Check this box if the product is offered as a recurring subscription service."
    )
    subscription_plan_id = fields.Many2one(
        'brightloop.subscription.plan',
        string="Default Subscription Plan",
        help="Optional default plan pre-selected when this product is quoted."
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_subscription_product = fields.Boolean(
        string="Can be Subscribed",
        related='product_tmpl_id.is_subscription_product',
        store=True,
        index=True
    )
