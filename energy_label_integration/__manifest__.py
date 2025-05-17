# -*- coding: utf-8 -*-
{
    'name': "Energy Label Integration (EP-Online & BAG PDOK)",
    'version': '1.0.0',
    'category': 'Sales/CRM',
    'summary': "Fetch Dutch energy label data for leads and quotations (EP-Online & BAG PDOK integration)",
    'description': """
This module adds fields for energy label information on CRM leads and quotations, 
and fetches data from EP-Online and BAG (PDOK) APIs.
""",

    'author': "Klimaat Techniek Holland B.V.",
    'website': "http://www.klimaattechniekholland.nl",
    'license': "LGPL-3",
    'depends': ['crm', 'sale', 'sale_management'],

    'data': [
        'data/crm_stages.xml',
        'views/energy_label_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    
    'installable': True,
    'application': False,
}

