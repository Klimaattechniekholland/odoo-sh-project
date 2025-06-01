# -*- coding: utf-8 -*-
{
    'name': "EP-Online & BAG PDOK Energy Label Integration",
    'version': '1.0',
    'summary': 'Integrates Dutch EP-Online and BAG APIs for energy labels',
    'description': """
Fetches energy label and building data from RVO EP-Online and Kadaster BAG APIs,
with fallback and manual refresh, as per specification.
    """,

    'author': "Klimaat Techniek Holland B.V.",
    'website': "http://www.klimaattechniekholland.nl",
    'license': "LGPL-3",
    'depends': ['base','crm','sale','contacts','sale_management',],
    'category': 'Sales/CRM',
    'external_dependencies': {
    #'python': ['httpx', 'pydantic'],
    },
    'data': [
        #'security/ir.model.access.csv',
        'data/stages.xml',
        'data/system_parameters.xml',
        #'views/crm_lead_views.xml',
        #'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/settings_views.xml',
    ],
  
    
    
    'installable': True,
    'application': False,
    'auto_install': True,
    # Define a post-init hook to fold default CRM stages after installing this module
    'post_init_hook': 'hooks.post_init_hook',
}

