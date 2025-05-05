{
    'name': 'AI Integration',
    'version': '18.0.1.0.0',
    'summary': 'Integrate an AI assistant into Odoo',
    'description': """
AI Integration
==============

This module provides an AI assistant integration into Odoo, allowing users to send prompts and receive responses from a configured LLM provider (e.g., OpenAI).
""",
    'author': 'Your Company',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'views/ai_config_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_integration/static/src/js/ai_widget.js',
            'ai_integration/static/src/xml/ai_widget_templates.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}