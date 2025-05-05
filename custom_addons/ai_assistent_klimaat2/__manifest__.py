{
    'name': 'AI Developer Assistent',
    'version': '1.2',
    'summary': 'Contextgevoelige AI-assistent voor Odoo v18',
    'category': 'Tools',
    'author': 'Klimaat Techniek Holland',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'web_enterprise',
    ],
    'data': [
        'data/ir_model.xml',
        'security/ir.model.access.csv',
        'views/ai_assistant_settings_views.xml',
        'views/ai_assistant_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_assistent_klimaat2/static/src/js/ai_assistant_popup.js',
            'ai_assistent_klimaat2/static/src/xml/ai_assistant_popup.xml',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}
