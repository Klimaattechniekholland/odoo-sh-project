# -*- coding: utf-8 -*-
{
    'name': 'Custom Sale Document',
    'summary': "Enhanced quotation/invoice reports, custom fields, QR codes, email templates, and contract generation",
    'description': "Adds multi-page quotation and invoice layouts (client info, house photo, system description, kit details, terms), custom fields on Sale Orders and Invoices, QR code support for signing, partner-language email templates, and a dynamic service contract wizard.",
    'author': "Klimaat Techniek Holland B.V.",
    'website': "http://www.klimaattechniekholland.nl",
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'account', 'mrp', 'mail', 'sale_pdf_quote_builder'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/mrp_bom_views.xml',
        'views/product_template_views.xml',
        'reports/report_saleorder.xml',
        'reports/report_invoice.xml',
        #'reports/report_service_contract.xml',
        #'data/email_templates.xml',
        #'data/report_actions.xml',
    ],
    'demo': [
        #'demo/demo_data.xml',
    ],
    
    'installable': True,
    'application': False,
}


