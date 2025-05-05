from odoo import models, fields, api

class AIConfig(models.TransientModel):
    _name = 'ai_integration.config'
    _inherit = 'res.config.settings'

    api_key = fields.Char(string="AI API Key")

    @api.model
    def get_values(self):
        res = super().get_values()
        config = self.env['ir.config_parameter'].sudo()
        res['api_key'] = config.get_param('ai_integration.api_key', default='')
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('ai_integration.api_key', self.api_key or '')
