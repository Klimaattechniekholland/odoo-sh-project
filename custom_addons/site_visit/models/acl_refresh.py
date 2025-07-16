import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ACLRefreshWizard(models.TransientModel):
    _name = 'site_visit.acl.refresh'
    _description = 'ACL Refresh Wizard for Site Visit'

    group_id = fields.Many2one('res.groups', string="Apply to Group", required=True)

    def refresh_acls(self):
        group = self.group_id

        _logger.info(f"🔁 Refreshing ACLs for group: {group.name}")

        models = self.env['ir.model'].search([('modules', '=', 'site_visit')])

        for model in models:
            _logger.info(f"🔍 Found model from site_visit: {model.model}")

            acl_vals = {
                'name': f'{model.model} access for {group.name}',
                'model_id': model.id,
                'group_id': group.id,
                'perm_read': True,
                'perm_write': group.name == 'Administration',
                'perm_create': group.name == 'Administration',
                'perm_unlink': group.name == 'Administration',
            }

            existing = self.env['ir.model.access'].search([
                ('model_id', '=', model.id),
                ('group_id', '=', group.id)
            ], limit=1)

            if existing:
                existing.write(acl_vals)
                _logger.info(f"✅ Updated ACL for {model.model} ({group.name})")
            else:
                self.env['ir.model.access'].create(acl_vals)
                _logger.info(f"✅ Created ACL for {model.model} ({group.name})")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'ACLs Updated',
                'message': f'Access rights updated for group: {group.name}',
                'sticky': False,
                'type': 'success',
            }
        }
