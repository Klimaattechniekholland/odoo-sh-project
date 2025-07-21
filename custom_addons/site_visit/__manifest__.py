{
	'name': 'site_visit',
	'version': '0.9',
	'summary': 'Site Visit with Images by System',
	'category': 'Tools',
	'author': 'Pi-Con',
	'website': 'https://www.pi-con.nl',
	
	'depends': ['base', 'base_setup','web', 'mail'],
	'post_init_hook': 'setup_site_visit_rights',
	
	'data': [
		
		'security/ir.model.access.csv',
		
		'data/email_template.xml',
		'data/automated_email.xml',
		
		
		'views/actions.xml',
		
		'views/acl_refresh_wizard.xml',
		
		'views/menu.xml',
		
		'views/site_visit_inspection_category_views.xml',
		'views/site_visit_inspection_component_views.xml',
		'views/site_visit_inspection_point_views.xml',
		
		'views/site_visit_template_structure_views.xml',
		'views/installation.xml',
		
		'views/site_visit_image_views.xml',
		'views/site_visit_views.xml',
		
		# 'demo/demo_data.xml',
		'report/report_site_visit_templates.xml',
		'report/report_site_visit_action.xml'
		],
	
	'icon': '/site_visit/static/description/icon.png',
	
	'installable': True,
	'application': True,
	'auto_install': False,
	'license': 'LGPL-3',
	'i18n': ['i18n/site_visit.pot']
	}
