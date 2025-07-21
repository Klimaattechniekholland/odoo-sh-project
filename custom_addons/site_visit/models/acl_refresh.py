
from odoo import models, fields
from odoo.exceptions import UserError
from ..utils.acl_tools import apply_acl_rules

class ACLRefresh(models.TransientModel):
    _name = 'site_visit.acl.refresh'
    _description = 'ACL Refresh Wizard for Site Visit'

    group_id = fields.Many2one('res.groups', string="Group", required=True)
    mode = fields.Selection([
        ('preview', 'Preview only'),
        ('apply', 'Apply now'),
    ], default='preview', required=True, string="Mode")

    preview_log = fields.Text(readonly=True)

    def refresh_acls(self):
        if not self.group_id:
            raise UserError("Please select a group.")

        group = self.group_id
        is_admin = group.get_external_id().get(group.id, '') == 'base.group_system'

        preview_lines = []
        models = self.env['ir.model'].search([('model', 'like', 'site.visit.%')])
        

        for model in models:
            if not model.model:
                continue

            existing = self.env['ir.model.access'].search([
                ('model_id', '=', model.id),
                ('group_id', '=', group.id)
            ], limit=1)

            if existing:
                preview_lines.append(f"Would update: {model.model}")
            else:
                preview_lines.append(f"Would create: {model.model}")

        if self.mode == 'preview':
            self.preview_log = "\n".join(preview_lines)
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

        # Apply mode
        apply_acl_rules(self.env, group, is_admin=is_admin)
        return {'type': 'ir.actions.act_window_close'}

