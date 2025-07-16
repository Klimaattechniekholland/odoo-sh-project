import logging


_logger = logging.getLogger(__name__)


def setup_site_visit_rights(env):
	_logger.info("🔧 Running post_init_hook to configure ACLs for site_visit models")
	
	group = env.ref('base.group_system', raise_if_not_found = False)
	if not group:
		_logger.warning("❌ Could not find group 'base.group_system'")
		return
	
	# Search all models starting with site_visit or defined under your module
	model_names = [
		'site.visit',
		'site.visit.inspection.category',
		'site.visit.inspection.component',
		'site.visit.inspection.point',
		'site.visit.inspection.image'
		'site.visit.inspection.image.point',
		]
	
	models = env['ir.model'].search(
		[
			('model', 'in', model_names)
			]
		)
	
	# models = env['ir.model'].search([
	#     ('model', 'ilike', 'site.visit.%')  # or use 'site.%', etc.
	# ])
	
	if not models:
		_logger.warning("⚠️ No models found matching 'site_visit%'")
		return
	
	for model in models:
		_logger.info(f"🔍 Setting up ACL for model: {model.model}")
		
		acl = env['ir.model.access'].search(
			[
				('model_id', '=', model.id),
				('group_id', '=', group.id)
				], limit = 1
			)
		
		acl_vals = {
			'name': f'{model.model} admin access',
			'model_id': model.id,
			'group_id': group.id,
			'perm_read': True,
			'perm_write': True,
			'perm_create': True,
			'perm_unlink': True,
			}
		
		if acl:
			acl.write(acl_vals)
			_logger.info(f"✅ Updated ACL for {model.model}")
		else:
			env['ir.model.access'].create(acl_vals)
			_logger.info(f"✅ Created new ACL for {model.model}")
