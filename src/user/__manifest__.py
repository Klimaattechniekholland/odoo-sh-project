{
    "name": "AI Developer Assistent",
    "version": "1.0",
    "category": "Tools",
    "summary": "Een AI-assistent die Odoo-code kan genereren en aanpassen via GPT/Gemini",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_model.xml",
        "views/ai_assistant_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "ai_assistant_klimaat2/static/src/js/ai_assistant_popup.js",
            "ai_assistant_klimaat2/static/src/xml/ai_assistant_popup.xml"
        ]
    },
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "auto_install": False
}