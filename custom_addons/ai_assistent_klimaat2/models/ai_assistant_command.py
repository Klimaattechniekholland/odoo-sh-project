from odoo import models, fields

class AIAssistantCommand(models.Model):
    _name = 'x_ai_assistant_command'
    _description = 'AI Assistant Command'

    name = fields.Char(string='Naam', required=True)
    description = fields.Text(string='Beschrijving')
