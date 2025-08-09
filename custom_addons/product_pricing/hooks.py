import logging

from .utils.access import safe_get_or_create_group

_logger = logging.getLogger(__name__)

def apply_acl_rules(env, group, is_admin=False):
    models = env['ir.model'].search([('model', 'ilike', 'product.pricing%')])
    for model in models:
        # --- ACL
        acl_vals = {
            'name': f"{model.model} access for {group.name}",
            'model_id': model.id,
            'group_id': group.id,
            'perm_read': True,
            'perm_write': is_admin,
            'perm_create': is_admin,
            'perm_unlink': is_admin,
        }

        acl = env['ir.model.access'].sudo().search([
            ('model_id', '=', model.id),
            ('group_id', '=', group.id)
        ], limit=1)

        if acl:
            acl.write(acl_vals)
            _logger.info(f"🔁 Updated ACL for {model.model} / {group.name}")
        else:
            env['ir.model.access'].sudo().create(acl_vals)
            _logger.info(f"✅ Created ACL for {model.model} / {group.name}")

        # --- Optional: record rule
        if not is_admin:
            rule = env['ir.rule'].sudo().search([
                ('model_id', '=', model.id),
                ('groups', 'in', group.id)
            ], limit=1)

            if not rule:
                env['ir.rule'].sudo().create({
                    'name': f"{model.model} rule for {group.name}",
                    'model_id': model.id,
                    'groups': [(6, 0, [group.id])],
                    'domain_force': '[]',  # Full access
                    'perm_read': True,
                    'perm_write': is_admin,
                    'perm_create': is_admin,
                    'perm_unlink': is_admin,
                })
                _logger.info(f"🛡️ Created record rule for {model.model} / {group.name}")


def setup_access_rights(env):

    _logger.warning("✅ [HOOK] Environment prepared.")
    # Optional: define custom group XML IDs
    group_user = safe_get_or_create_group(env, 'base.group_user', name='Internal User')
    group_admin = safe_get_or_create_group(env, 'base.group_system', name='System Admin')

    apply_acl_rules(env, group_user, is_admin=False)
    apply_acl_rules(env, group_admin, is_admin=True)
