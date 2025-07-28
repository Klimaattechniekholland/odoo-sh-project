{
	'name': 'product_manager',
	'version': '1.0.0',
	'summary': 'Integrate Odoo with product management',
	'category': 'Tools',
	'author': 'Pi-Con',
	'website': 'https://www.pi-con.nl',
	'depends': [
		'base',
		'base_setup',
		'contacts',
		'product'
		],
	
	# 'post_init_hook': 'setup_bag_access_rights',
	
	'data': [
		# 'views/res_config_settings_view.xml',
		# 'views/res_partner_ep_online_view.xml',
		# 'views/res_partner_zip_fullnumber_view.xml',
		# 'views/res_partner_zip_bag_ep_button.xml' is added in the online view
		],
	
	# 'icon': '/bag_ep_api/static/description/kuwp.png',
	
	'installable': True,
	'application': True,
	'auto_install': True,
	
	'license': 'LGPL-3'
	}
