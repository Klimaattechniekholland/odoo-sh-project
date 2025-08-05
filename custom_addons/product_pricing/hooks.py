import logging

from odoo import api, SUPERUSER_ID


_logger = logging.getLogger(__name__)


def apply_acl_rules(env, group, is_admin = False):
	models = env['ir.model'].search([('model', '=', 'product.pricing')])
	for model in models:
		acl_vals = {
			'name': f"{model.model} access for {group.name}",
			'model_id': model.id,
			'group_id': group.id,
			'perm_read': True,
			'perm_write': is_admin,
			'perm_create': is_admin,
			'perm_unlink': is_admin,
			}
		existing = env['ir.model.access'].search(
			[
				('model_id', '=', model.id),
				('group_id', '=', group.id)
				], limit = 1
			)
		if existing:
			existing.write(acl_vals)
			_logger.info(f"🔄 Updated ACL for {model.model}")
		else:
			env['ir.model.access'].create(acl_vals)
			_logger.info(f"✅ Created ACL for {model.model}")


# ✅ Correct hybrid hook function
def setup_access_rights(*args):
	if len(args) == 1 and hasattr(args[0], 'cr'):
		# Odoo 18+
		env = args[0]
	else:
		# Odoo <= 17
		cr, registry = args
		env = api.Environment(cr, SUPERUSER_ID, {})
	
	group_user = env.ref('base.group_user')
	group_admin = env.ref('base.group_system')
	
	apply_acl_rules(env, group_user, is_admin = False)
	apply_acl_rules(env, group_admin, is_admin = True)
