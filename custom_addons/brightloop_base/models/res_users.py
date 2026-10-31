# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import AccessError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure that only Brightloop Administrators can create internal staff members."""
        for vals in vals_list:
            self._check_brightloop_staff_management_rights(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Ensure that only Brightloop Administrators can modify or assign staff privileges."""
        self._check_brightloop_staff_management_rights(vals)
        return super().write(vals)

    def _check_brightloop_staff_management_rights(self, vals):
        """Validates that internal staff or admin assignments require Brightloop Admin role."""
        if self.env.is_superuser():
            return

        if self.env.user.has_group('brightloop_base.group_brightloop_admin'):
            return

        admin_group = self.env.ref('brightloop_base.group_brightloop_admin', raise_if_not_found=False)
        staff_group = self.env.ref('brightloop_base.group_brightloop_user', raise_if_not_found=False)

        if not admin_group or not staff_group:
            return

        restricted_group_ids = {admin_group.id, staff_group.id}

        if 'group_ids' in vals:
            for command in vals['group_ids']:
                if isinstance(command, (list, tuple)):
                    cmd_type = command[0]
                    if cmd_type == 4:
                        if command[1] in restricted_group_ids:
                            raise AccessError(
                                _("Access Denied: Only Brightloop Administrators can assign internal staff or administrator roles.")
                            )
                    elif cmd_type == 6:
                        ids = set(command[2])
                        if ids & restricted_group_ids:
                            raise AccessError(
                                _("Access Denied: Only Brightloop Administrators can assign internal staff or administrator roles.")
                            )

        for user in self:
            if user.has_group('brightloop_base.group_brightloop_user') or user.has_group('brightloop_base.group_brightloop_admin'):
                if 'group_ids' in vals or 'active' in vals:
                    raise AccessError(
                        _("Access Denied: Only Brightloop Administrators can modify internal staff user accounts.")
                    )
