{
    'name': 'AI Developer Assistent',
    'version': '1.3',
    'summary': 'Contextgevoelige AI-assistent voor Odoo v18 via Wizard',
    'category': 'Tools',
    'author': 'Klimaat Techniek Holland',
    'license': 'AGPL-3',
    'depends': ['base', 'web', 'web_enterprise'],
    'data': [
        'data/ir_model.xml',
        'security/ir.model.access.csv',
        'views/ai_assistant_settings_views.xml',
        'views/ai_assistant_views.xml',
        'views/ai_prompt_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}