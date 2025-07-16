from odoo import models, fields
from odoo.exceptions import UserError
from ..utils.acl_tools import apply_acl_rules

class ACLRefresh(models.TransientModel):
    _name = 'site_visit.acl.refresh'
    _description = 'ACL Refresh Wizard for Site Visit'

    group_id = fields.Many2one('res.groups', string="Group", required=True)

    def refresh_acls(self):
        if not self.group_id:
            raise UserError("Please select a group.")

        group = self.group_id
        is_admin = group.get_external_id().get(group.id, '') == 'base.group_system'
        apply_acl_rules(self.env, group, is_admin=is_admin)

        return {'type': 'ir.actions.act_window_close'}