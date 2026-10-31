# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError, AccessError


@tagged('post_install', '-at_install', 'brightloop_sub')
class TestBrightloopSubscription(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_group = cls.env.ref('brightloop_base.group_brightloop_admin')
        cls.staff_group = cls.env.ref('brightloop_base.group_brightloop_user')
        cls.portal_group = cls.env.ref('brightloop_base.group_brightloop_portal')

        # Admin user
        cls.admin_user = cls.env['res.users'].create({
            'name': 'Subscription Test Admin',
            'login': 'sub_admin@brightloop.test',
            'email': 'sub_admin@brightloop.test',
            'group_ids': [(6, 0, [cls.admin_group.id])],
        })

        # Internal staff user
        cls.staff_user = cls.env['res.users'].create({
            'name': 'Subscription Test Staff',
            'login': 'sub_staff@brightloop.test',
            'email': 'sub_staff@brightloop.test',
            'group_ids': [(6, 0, [cls.staff_group.id])],
        })

        # Customer partner and portal user
        cls.partner_customer = cls.env['res.partner'].create({
            'name': 'Brightloop Client Alpha',
            'email': 'client_alpha@brightloop.test',
        })
        cls.customer_user = cls.env['res.users'].create({
            'name': 'Client Alpha User',
            'login': 'client_alpha@brightloop.test',
            'email': 'client_alpha@brightloop.test',
            'partner_id': cls.partner_customer.id,
            'group_ids': [(6, 0, [cls.portal_group.id])],
        })

        # Base Product Setup
        cls.product_template = cls.env['product.template'].create({
            'name': 'Cloud ERP Platform',
            'type': 'service',
            'list_price': 1000.0,
            'standard_price': 300.0,
            'description': 'Cloud ERP Subscription Core',
            'is_subscription_product': True,
        })

        # Attribute Setup: Brand with Odoo (+560.00)
        cls.brand_attribute = cls.env['product.attribute'].create({
            'name': 'Brand',
            'value_ids': [
                (0, 0, {'name': 'Standard'}),
                (0, 0, {'name': 'Odoo'}),
            ]
        })
        cls.val_standard = cls.brand_attribute.value_ids.filtered(lambda v: v.name == 'Standard')
        cls.val_odoo = cls.brand_attribute.value_ids.filtered(lambda v: v.name == 'Odoo')

        # Link attribute to template
        cls.ptal = cls.env['product.template.attribute.line'].create({
            'product_tmpl_id': cls.product_template.id,
            'attribute_id': cls.brand_attribute.id,
            'value_ids': [(6, 0, [cls.val_standard.id, cls.val_odoo.id])],
        })
        # Set price extra = 560.00 on the Odoo attribute value
        ptav_odoo = cls.ptal.product_template_value_ids.filtered(lambda ptav: ptav.product_attribute_value_id == cls.val_odoo)
        ptav_odoo.write({'price_extra': 560.0})

        # Variants
        cls.variant_standard = cls.product_template.product_variant_ids.filtered(
            lambda p: cls.val_standard in p.product_template_variant_value_ids.product_attribute_value_id
        )
        cls.variant_odoo = cls.product_template.product_variant_ids.filtered(
            lambda p: cls.val_odoo in p.product_template_variant_value_ids.product_attribute_value_id
        )

        # Standard Monthly Plan
        cls.plan_monthly = cls.env['brightloop.subscription.plan'].create({
            'name': 'Monthly Professional',
            'billing_unit': 'month',
            'billing_interval': 1,
            'min_quantity': 2.0,
            'allow_early_closure': True,
            'allow_pause': True,
            'allow_renewal': True,
            'auto_close_on_expiry': True,
        })

    # 1. Product Creation Test
    def test_01_product_creation(self):
        """Verify product template creation with subscription flag."""
        self.assertEqual(self.product_template.name, 'Cloud ERP Platform')
        self.assertEqual(self.product_template.list_price, 1000.0)
        self.assertTrue(self.product_template.is_subscription_product)

    # 2. Product Variant Creation Test
    def test_02_product_variant_creation(self):
        """Verify two variants generated for Standard and Odoo brands."""
        self.assertEqual(len(self.product_template.product_variant_ids), 2)
        self.assertTrue(self.variant_standard)
        self.assertTrue(self.variant_odoo)

    # 3. Variant Price Extra Test (1000 + 560 = 1560)
    def test_03_variant_price_extra(self):
        """Verify that choosing Odoo brand adds 560.00 to the base price."""
        self.assertEqual(self.variant_standard.lst_price, 1000.0)
        self.assertEqual(self.variant_odoo.lst_price, 1560.0)

    # 4. Plan Creation Test
    def test_04_plan_creation(self):
        """Verify plan creation with operational flags."""
        self.assertEqual(self.plan_monthly.billing_unit, 'month')
        self.assertEqual(self.plan_monthly.billing_interval, 1)
        self.assertEqual(self.plan_monthly.min_quantity, 2.0)
        self.assertTrue(self.plan_monthly.allow_pause)

    # 5. Daily Recurrence Calculation Test
    def test_05_daily_recurrence(self):
        """Verify daily recurrence calculates next billing date as +N days."""
        plan_daily = self.env['brightloop.subscription.plan'].create({
            'name': 'Daily Trial',
            'billing_unit': 'day',
            'billing_interval': 3,
        })
        start = date(2026, 11, 1)
        next_date = plan_daily.calculate_next_billing_date(start)
        self.assertEqual(next_date, date(2026, 11, 4))

    # 6. Weekly Recurrence Calculation Test
    def test_06_weekly_recurrence(self):
        """Verify weekly recurrence calculates next billing date as +N weeks."""
        plan_weekly = self.env['brightloop.subscription.plan'].create({
            'name': 'Bi-Weekly Plan',
            'billing_unit': 'week',
            'billing_interval': 2,
        })
        start = date(2026, 11, 1)
        next_date = plan_weekly.calculate_next_billing_date(start)
        self.assertEqual(next_date, date(2026, 11, 15))

    # 7. Monthly Recurrence Calculation Test
    def test_07_monthly_recurrence(self):
        """Verify monthly recurrence calculation."""
        start = date(2026, 11, 1)
        next_date = self.plan_monthly.calculate_next_billing_date(start)
        self.assertEqual(next_date, date(2026, 12, 1))

    # 8. Yearly Recurrence Calculation Test
    def test_08_yearly_recurrence(self):
        """Verify yearly recurrence calculation."""
        plan_yearly = self.env['brightloop.subscription.plan'].create({
            'name': 'Annual Enterprise',
            'billing_unit': 'year',
            'billing_interval': 1,
        })
        start = date(2026, 11, 1)
        next_date = plan_yearly.calculate_next_billing_date(start)
        self.assertEqual(next_date, date(2027, 11, 1))

    # 9. Minimum Quantity Enforcement Test
    def test_09_minimum_quantity_enforcement(self):
        """Verify that quotation creation blocks quantities below plan MOQ."""
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,  # MOQ = 2.0
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 1.0,  # Below minimum!
                'price_unit': 1560.0,
            })],
        })
        with self.assertRaises(ValidationError):
            sub.action_to_quotation()

    # 10. Plan Availability Dates Test
    def test_10_plan_availability_dates(self):
        """Verify plan availability date window constraints."""
        plan_future = self.env['brightloop.subscription.plan'].create({
            'name': 'Future Black Friday Plan',
            'billing_unit': 'month',
            'date_start': date(2026, 11, 20),
            'date_end': date(2026, 11, 30),
        })
        self.assertFalse(plan_future.is_available_on(date(2026, 11, 1)))
        self.assertTrue(plan_future.is_available_on(date(2026, 11, 25)))
        self.assertFalse(plan_future.is_available_on(date(2026, 12, 1)))

    # 11. Quotation Templates Test
    def test_11_quotation_template(self):
        """Verify quotation template applies plan, validity date, and lines."""
        template = self.env['brightloop.quotation.template'].create({
            'name': 'Standard Odoo Template',
            'plan_id': self.plan_monthly.id,
            'validity_days': 14,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 3.0,
                'price_unit': 1560.0,
            })],
        })
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'template_id': template.id,
        })
        self.assertEqual(sub.plan_id, self.plan_monthly)
        self.assertEqual(len(sub.line_ids), 1)
        self.assertEqual(sub.line_ids.price_unit, 1560.0)
        self.assertEqual(sub.line_ids.quantity, 3.0)

    # 12. Subscription Creation Test
    def test_12_subscription_creation(self):
        """Verify subscription creation in Draft state with correct totals."""
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 2.0,
                'price_unit': 1560.0,
            })],
        })
        self.assertEqual(sub.state, 'draft')
        self.assertEqual(sub.amount_untaxed, 3120.0)
        self.assertEqual(sub.amount_total, 3120.0)

    # 13. Lifecycle Transitions: Draft -> Quotation -> Confirmed -> Active -> Closed
    def test_13_subscription_lifecycle(self):
        """Verify the full 5-stage lifecycle state machine."""
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 2.0,
                'price_unit': 1560.0,
            })],
        })
        # Draft -> Quotation
        sub.action_to_quotation()
        self.assertEqual(sub.state, 'quotation')
        self.assertNotEqual(sub.name, 'New')

        # Quotation -> Confirmed
        sub.action_confirm()
        self.assertEqual(sub.state, 'confirmed')

        # Confirmed -> Active
        sub.action_activate()
        self.assertEqual(sub.state, 'active')
        self.assertTrue(sub.next_billing_date)

        # Active -> Closed
        sub.action_close(reason='Customer Completed Contract')
        self.assertEqual(sub.state, 'closed')
        self.assertEqual(sub.close_reason, 'Customer Completed Contract')

    # 14. Pause and Resume Workflow
    def test_14_pause_and_resume(self):
        """Verify pause and resume controls on active subscriptions."""
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 2.0,
                'price_unit': 1560.0,
            })],
        })
        sub.action_to_quotation()
        sub.action_confirm()
        sub.action_activate()

        # Pause
        sub.action_pause()
        self.assertTrue(sub.is_paused)
        self.assertFalse(sub.is_eligible_for_billing)

        # Resume
        sub.action_resume()
        self.assertFalse(sub.is_paused)

    # 15. Subscription Renewal Test
    def test_15_renewal(self):
        """Verify renewal creates a linked draft subscription."""
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 2.0,
                'price_unit': 1560.0,
            })],
        })
        sub.action_to_quotation()
        sub.action_confirm()
        sub.action_activate()

        res = sub.action_renew()
        renewal_id = res['res_id']
        renewal_sub = self.env['brightloop.subscription'].browse(renewal_id)
        self.assertEqual(renewal_sub.origin_subscription_id, sub)
        self.assertEqual(renewal_sub.state, 'draft')
        self.assertEqual(len(renewal_sub.line_ids), 1)

    # 16. Early Closure Permission Enforcement
    def test_16_early_closure_permission(self):
        """Verify early closure is prohibited if plan disallows it."""
        strict_plan = self.env['brightloop.subscription.plan'].create({
            'name': 'Strict Lock-in Annual',
            'billing_unit': 'year',
            'allow_early_closure': False,
        })
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': strict_plan.id,
            'expiry_date': date(2027, 12, 31),
            'line_ids': [(0, 0, {
                'product_id': self.variant_standard.id,
                'name': self.variant_standard.display_name,
                'quantity': 1.0,
                'price_unit': 1000.0,
            })],
        })
        sub.action_to_quotation()
        sub.action_confirm()
        sub.action_activate()

        with self.assertRaises(UserError):
            sub.action_close()

    # 17. Automatic Closure Cron Test
    def test_17_automatic_closure(self):
        """Verify cron auto-closes active subscriptions reaching expiry date."""
        yesterday = fields.Date.context_today(self) - relativedelta(days=1)
        sub = self.env['brightloop.subscription'].create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,
            'expiry_date': yesterday,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 2.0,
                'price_unit': 1560.0,
            })],
        })
        sub.action_to_quotation()
        sub.action_confirm()
        sub.action_activate()

        self.env['brightloop.subscription'].cron_auto_close_expired()
        self.assertEqual(sub.state, 'closed')

    # 18. Role-Based Access Control Test
    def test_18_role_based_access(self):
        """Verify internal staff can manage subscriptions but cannot edit plans."""
        sub = self.env['brightloop.subscription'].with_user(self.staff_user).create({
            'partner_id': self.partner_customer.id,
            'plan_id': self.plan_monthly.id,
            'line_ids': [(0, 0, {
                'product_id': self.variant_odoo.id,
                'name': self.variant_odoo.display_name,
                'quantity': 2.0,
                'price_unit': 1560.0,
            })],
        })
        self.assertTrue(sub.id)

        # Staff cannot modify or create plans
        with self.assertRaises(AccessError):
            self.plan_monthly.with_user(self.staff_user).write({'min_quantity': 10.0})
