{
	'name': 'bag_ep_api',
	'version': '1.0.0',
	'summary': 'Integrate Odoo with the BAG API',
	'category': 'Tools',
	'author': 'Pi-Con',
	'website': 'https://www.pi-con.nl',
	'depends': [
		'base',
		'base_setup',
		'contacts',
		],
	
	'post_init_hook': 'setup_bag_access_rights',
	
	'data': [
		'views/res_config_settings_view.xml',
		'views/res_partner_ep_online_view.xml',
		'views/res_partner_zip_full_number_view.xml',
		],
	
	'icon': '/bag_ep_api/static/description/kuwp.png',

	
	'installable': True,
	'application': True,
	'auto_install': True,

	'license': 'LGPL-3'
	}
