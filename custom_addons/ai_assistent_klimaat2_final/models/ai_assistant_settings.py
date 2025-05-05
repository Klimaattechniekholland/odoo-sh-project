from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AISettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openai_api_key = fields.Char(string='OpenAI API Key', config_parameter='ai_assistant.openai_key')
    gemini_api_key = fields.Char(string='Gemini API Key', config_parameter='ai_assistant.gemini_key')

    @api.constrains('openai_api_key', 'gemini_api_key')
    def _check_keys(self):
        for rec in self:
            for fld in ['openai_api_key', 'gemini_api_key']:
                key = getattr(rec, fld)
                if key and len(key) < 20:
                    raise ValidationError(f"{fld.replace('_', ' ').title()} lijkt te kort.")
