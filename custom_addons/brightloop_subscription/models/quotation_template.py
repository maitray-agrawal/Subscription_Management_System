# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BrightloopQuotationTemplate(models.Model):
    _name = 'brightloop.quotation.template'
    _description = 'Subscription Quotation Template'
    _order = 'name'

    name = fields.Char(string="Template Name", required=True, translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    plan_id = fields.Many2one(
        'brightloop.subscription.plan',
        string="Subscription Plan",
        required=True,
        help="Default plan linked to this quotation template."
    )
    validity_days = fields.Integer(
        string="Quotation Validity (Days)",
        default=30,
        required=True,
        help="Number of days before an issued quotation expires."
    )
    line_ids = fields.One2many(
        'brightloop.quotation.template.line',
        'template_id',
        string="Template Lines",
        copy=True
    )
    note = fields.Html(string="Terms & Conditions")

    _check_validity_days = models.Constraint(
        'CHECK(validity_days > 0)',
        'Quotation validity duration must be greater than zero days.'
    )


class BrightloopQuotationTemplateLine(models.Model):
    _name = 'brightloop.quotation.template.line'
    _description = 'Quotation Template Line'
    _order = 'id'

    template_id = fields.Many2one(
        'brightloop.quotation.template',
        string="Template",
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True,
        domain=[('sale_ok', '=', True)]
    )
    name = fields.Text(string="Description", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    price_unit = fields.Float(string="Unit Price", required=True, default=0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            # lst_price in Odoo automatically includes product variant extra prices
            self.price_unit = self.product_id.lst_price
