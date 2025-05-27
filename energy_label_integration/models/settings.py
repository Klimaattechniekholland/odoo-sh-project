# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ep_online_api_key = fields.Char(
        string="EP-Online API Key",
        config_parameter="energy_label_integration.ep_online_api_key",
        help="API key for RVO EP-Online service (energy labels)."
    )
    bag_api_key = fields.Char(
        string="BAG API Key",
        config_parameter="energy_label_integration.bag_api_key",
        help="API key for Kadaster BAG individual queries."
    )
