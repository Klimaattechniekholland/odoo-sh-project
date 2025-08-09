

{
	'name': 'Product Pricing',
	'version': '1.0.0',
	'summary': 'Integrate Odoo with product management',
	'category': 'Tools',
	'author': 'Pi-Con',
	'website': 'https://www.pi-con.nl',
	'depends': [
		'base',
		'base_setup',
		'contacts',
		'product',
		'purchase'
		],
	
	'post_init_hook': 'setup_access_rights',

	'data': [
		
		'views/product_template_product_pricing_view.xml',
		'views/product_template_optional_columns.xml',
		'views/product_pricing_mass_wizard.xml',
		'views/product_pricing_mass_action.xml',
		
		],
	
	'installable': True,
	'application': True,
	'auto_install': False,
	
	'license': 'LGPL-3'
	}
