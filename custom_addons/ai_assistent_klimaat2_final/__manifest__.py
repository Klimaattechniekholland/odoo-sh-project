{
    'name': 'AI Developer Assistent',
    'version': '1.1',
    'summary': 'Contextgevoelige AI-assistent voor Odoo v18',
    'category': 'Tools',
    'author': 'Klimaat Techniek Holland',
    'license': 'AGPL-3',
    'depends': ['base', 'web', 'web_enterprise'],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_assistant_settings_views.xml',
        'views/ai_assistant_views.xml',
        'data/ir_model.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'static/src/js/ai_assistant_popup.js',
            'static/src/xml/ai_assistant_popup.xml',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}