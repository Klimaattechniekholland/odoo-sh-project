import logging


_logger = logging.getLogger(__name__)


def apply_acl_rules(env, group, is_admin = False):
	
	models = env['ir.model'].search([('model', 'like', 'site.visit.%')])
	
	if not models:
		_logger.warning("⚠ No models found for module 'site_visit'")
		return
	
	for model in models:
		if not model.model:
			continue
		
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
