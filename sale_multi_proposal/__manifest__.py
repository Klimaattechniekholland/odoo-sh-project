{
    'name': 'Sale Multi Proposal',
    'version': '18.0.1.0.0',
    'author': 'Your Company',
    'license': 'LGPL-3',
    'category': 'Sales',
    'website': 'https://example.com',
    'summary': 'Allow multiple proposals per sale order and prevent partner address loops',
    'description': 'This module extends the Sale application to support multiple proposals '
                   'within a single sale order.  Sales people can add several alternative '
                   'proposal lines to a sale order and customers may choose one to confirm. '
                   'The module also adds a constraint on partners to avoid recursive parent–child '
                   'relationships (address loops).',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_proposition_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}