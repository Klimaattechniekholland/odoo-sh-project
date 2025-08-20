import logging

_logger = logging.getLogger(__name__)

def setup_bag_access_rights(env):
    _logger.info("post_init_hook is running")

    model = env['ir.model'].search([('model', '=', 'ep.data')], limit=1)
    group = env.ref('base.group_system', raise_if_not_found=False)

    if not model or not group:
        _logger.warning("❌ Could not find model 'ep.data' or group 'base.group_system'")
        return

    acl = env['ir.model.access'].search([
        ('model_id', '=', model.id),
        ('group_id', '=', group.id)
    ], limit=1)

    acl_vals = {
        'name': 'ep.data admin access',
        'model_id': model.id,
        'group_id': group.id,
        'perm_read': True,
        'perm_write': True,
        'perm_create': True,
        'perm_unlink': True,
    }

    if acl:
        acl.write(acl_vals)
        _logger.info("Updated existing ACL for ep.data")
    else:
        env['ir.model.access'].create(acl_vals)
        _logger.info("Created new ACL for ep.data")
