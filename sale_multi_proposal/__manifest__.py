{
    'name': 'Sale Multi Proposal',
    'summary': 'Allow multiple proposals per sale order',
    'description': "Allow multiple proposals per sale order",
    'author': "Klimaat Techniek Holland B.V.",
    'website': "http://www.klimaattechniekholland.nl",
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale', 'sale_management'],
    'data': [
        
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizards/proposal_accept_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}