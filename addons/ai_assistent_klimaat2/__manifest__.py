{
    "name": "AI Developer Assistent",
    "version": "1.0",
    "category": "Tools",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/ai_assistant_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "ai_assistant_klimaat2/static/src/js/ai_assistant_popup.js",
            "ai_assistant_klimaat2/static/src/xml/ai_assistant_popup.xml"
        ]
    },
    "installable": True,
    "application": True,
    "auto_install": False
}