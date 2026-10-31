# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'brightloop_security')
class TestBrightloopSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_portal = cls.env.ref('brightloop_base.group_brightloop_portal')
        cls.group_staff = cls.env.ref('brightloop_base.group_brightloop_user')
        cls.group_admin = cls.env.ref('brightloop_base.group_brightloop_admin')
        cls.group_internal_user = cls.env.ref('base.group_user')
        cls.group_base_portal = cls.env.ref('base.group_portal')
        cls.group_system = cls.env.ref('base.group_system')

        # Admin user
        cls.admin_user = cls.env['res.users'].create({
            'name': 'Brightloop Test Admin',
            'login': 'test_bl_admin@brightloop.test',
            'email': 'test_bl_admin@brightloop.test',
            'group_ids': [(6, 0, [cls.group_admin.id])],
        })

        # Internal staff user (no admin rights)
        cls.staff_user = cls.env['res.users'].create({
            'name': 'Brightloop Test Staff',
            'login': 'test_bl_staff@brightloop.test',
            'email': 'test_bl_staff@brightloop.test',
            'group_ids': [(6, 0, [cls.group_staff.id])],
        })

        # Customer portal user
        cls.customer_user = cls.env['res.users'].create({
            'name': 'Brightloop Test Customer',
            'login': 'test_bl_customer@brightloop.test',
            'email': 'test_bl_customer@brightloop.test',
            'group_ids': [(6, 0, [cls.group_portal.id])],
        })

    def test_01_group_hierarchy(self):
        """Verify group inheritance: Admin -> Staff -> Internal User; Customer -> Portal."""
        # Admin implies Staff
        self.assertIn(
            self.group_staff,
            self.group_admin.all_implied_ids,
            "group_brightloop_admin must imply group_brightloop_user"
        )
        # Admin implies base.group_system
        self.assertIn(
            self.group_system,
            self.group_admin.all_implied_ids,
            "group_brightloop_admin must imply base.group_system"
        )
        # Staff implies base.group_user
        self.assertIn(
            self.group_internal_user,
            self.group_staff.all_implied_ids,
            "group_brightloop_user must imply base.group_user"
        )
        # Customer implies base.group_portal
        self.assertIn(
            self.group_base_portal,
            self.group_portal.all_implied_ids,
            "group_brightloop_portal must imply base.group_portal"
        )

    def test_02_effective_user_membership(self):
        """Verify that assigned users have expected effective groups."""
        self.assertTrue(self.admin_user.has_group('brightloop_base.group_brightloop_admin'))
        self.assertTrue(self.admin_user.has_group('brightloop_base.group_brightloop_user'))
        self.assertTrue(self.staff_user.has_group('brightloop_base.group_brightloop_user'))
        self.assertFalse(self.staff_user.has_group('brightloop_base.group_brightloop_admin'))
        self.assertTrue(self.customer_user.has_group('brightloop_base.group_brightloop_portal'))
        self.assertFalse(self.customer_user.has_group('base.group_user'))

    def test_03_admin_can_create_staff(self):
        """Brightloop Administrator is authorized to create a new internal staff user."""
        new_staff = self.env['res.users'].with_user(self.admin_user).create({
            'name': 'New Hired Staff',
            'login': 'new_hired@brightloop.test',
            'email': 'new_hired@brightloop.test',
            'group_ids': [(6, 0, [self.group_staff.id])],
        })
        self.assertTrue(new_staff.has_group('brightloop_base.group_brightloop_user'))

    def test_04_staff_cannot_create_staff(self):
        """Internal Staff MUST NOT be able to create another internal staff user."""
        with self.assertRaises(AccessError):
            self.env['res.users'].with_user(self.staff_user).create({
                'name': 'Unauthorized Staff By Staff',
                'login': 'unauthorized_staff@brightloop.test',
                'email': 'unauthorized_staff@brightloop.test',
                'group_ids': [(4, self.group_staff.id)],
            })

    def test_05_staff_cannot_escalate_to_admin(self):
        """Internal Staff MUST NOT be able to grant admin privileges to anyone."""
        with self.assertRaises(AccessError):
            self.staff_user.with_user(self.staff_user).write({
                'group_ids': [(4, self.group_admin.id)],
            })

    def test_06_config_settings_parameters(self):
        """Verify that shared config settings save and retrieve correctly from ir.config_parameter."""
        settings = self.env['res.config.settings'].with_user(self.admin_user).create({
            'brightloop_auto_close_days': 21,
            'brightloop_invoice_auto_send': False,
            'brightloop_allow_daily_billing': True,
        })
        settings.execute()
        ICP = self.env['ir.config_parameter'].sudo()
        self.assertEqual(ICP.get_param('brightloop.auto_close_days'), '21')
        self.assertFalse(ICP.get_param('brightloop.invoice_auto_send'))
        self.assertEqual(ICP.get_param('brightloop.allow_daily_billing'), 'True')
