# -*- coding: utf-8 -*-
{
    'name': "EP-Online & BAG PDOK Energy Label Integration",
    'version': '1.0',
    'summary': 'Custom CRM module to integrate EP-Online & BAG PDOK for energy labels and custom CRM stages',
    'category': 'CRM',
    'description': """
                    This module adds fields for energy label information on CRM leads and quotations, 
                    and fetches data from EP-Online and BAG (PDOK) APIs.
                   """,

    'author': "Klimaat Techniek Holland B.V.",
    'website': "http://www.klimaattechniekholland.nl",
    'license': "LGPL-3",
    'depends': ['crm','sale', 'sale_management',],

    'data': [
        #'security/ir.model.access.csv',  
        #'data/crm_stage_data.xml',
        #'views/crm_energy_label_views.xml',
    ],
    
    
    'installable': True,
    'application': False,
    'auto_install': True,
    # Define a post-init hook to deactivate default CRM stages after installing this module
    # 'post_init_hook': 'post_init',
}

