import logging
from odoo import models

_logger = logging.getLogger(__name__)

class ACLRefresh(models.TransientModel):
    _name = 'site_visit.acl.refresh'
    _description = 'Refresh ACLs for Site Visit'

    def refresh_acls(self):
        _logger.info("🔁 Manually refreshing ACLs for models in module: site_visit")

        # Define groups to apply ACLs for
        target_groups = [
            self.env.ref('base.group_system', raise_if_not_found=False),
            self.env.ref('base.group_user', raise_if_not_found=False),
        ]

        # Get all models defined in this module
        models = self.env['ir.model'].search([('modules', '=', 'site_visit')])

        for model in models:
            _logger.info(f"🔍 Found model from site_visit: {model.model}")
            for group in target_groups:
                if not group:
                    continue

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

        return {'type': 'ir.actions.act_window_close'}
