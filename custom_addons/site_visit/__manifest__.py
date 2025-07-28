{
	'name': 'site_visit',
	'version': '0.9',
	'summary': 'Site Visit with Images by System',
	'category': 'Tools',
	'author': 'Pi-Con',
	'website': 'https://www.pi-con.nl',
	
	'depends': ['base', 'base_setup', 'web', 'mail'],
	'post_init_hook': 'setup_site_visit_rights',
	
	'data': [
		
		'security/ir.model.access.csv',
		
		'data/email_template.xml',
		'data/automated_email.xml',
		
		'views/actions.xml',
		'views/acl_refresh_wizard.xml',
		
		'views/menus/root_menu.xml',
		'views/menus/site_visit_menu.xml',
		'views/menus/configuration_menu.xml',
		'views/menus/developer_menu.xml',
		
		'views/inspection/site_visit_category_views.xml',
		'views/inspection/site_visit_component_views.xml',
		'views/inspection/site_visit_point_views.xml',
		'views/inspection/site_visit_image_views.xml',
		'views/inspection/site_visit_views.xml',
		
		'views/templates/site_visit_template_form.xml',
		'views/templates/site_visit_template_category_views.xml',
		'views/templates/site_visit_template_component_views.xml',
		'views/templates/site_visit_template_point_views.xml',
		'views/templates/site_visit_template_point_input_views.xml',
		
		"wizards/template_wizard.xml",
		"wizards/template_category_wizard.xml",
		"wizards/template_component_wizard.xml",
		"wizards/template_point_wizard.xml",
		"wizards/template_input_wizard.xml",
		
		# 'demo/demo_data.xml',
		
		'report/report_site_visit_templates.xml',
		'report/report_site_visit_action.xml'
		],
	
	"assets": {
		"web.assets_backend": [
			"site_visit/static/src/css/site_visit_styles.css",
			# "site_visit/static/src/breadcrumb.js"
			],
		},
	
	'icon': '/site_visit/static/description/icon.png',
	
	'installable': True,
	'application': True,
	'auto_install': False,
	'license': 'LGPL-3',
	'i18n': ['i18n/site_visit.pot']
	}
