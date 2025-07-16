from .utils.acl_tools import apply_acl_rules


def setup_site_visit_rights(env):
	group = env.ref('base.group_system', raise_if_not_found = False)
	
	if group:
		apply_acl_rules(env, group, is_admin = True)
