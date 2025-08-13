{
    'name': 'Sale Multi Proposal',
    'summary': 'Allow multiple proposals per sale order',
    'description': "Adds multi-page quotation and invoice layouts (client info, house photo, system description, kit details, terms), custom fields on Sale Orders and Invoices, QR code support for signing, partner-language email templates, and a dynamic service contract wizard.",
    'author': "Klimaat Techniek Holland B.V.",
    'website': "http://www.klimaattechniekholland.nl",
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}