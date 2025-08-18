# -*- coding: utf-8 -*-
"""
System configuration settings for the KTH Web Bridge module.
"""

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    kth_api_token = fields.Char(
        string="Web Leads API Token",
        config_parameter="kth_web_bridge.api_token",
        help=(
            "Bearer token used by WordPress/Forminator to authenticate calls to "
            "/api/web_leads.  Provide this token in the Authorization header "
            "(Bearer <token>) or in the query string (?token=<token>)."
        ),
    )

    