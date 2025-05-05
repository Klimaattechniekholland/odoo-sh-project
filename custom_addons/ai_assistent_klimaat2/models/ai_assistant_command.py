from odoo import models, fields

class AIAssistantCommand(models.Model):
    _name = 'ai.assistant.command'
    _description = 'AI Assistant Command'

    name = fields.Char(string='Naam', required=True)
    description = fields.Text(string='Beschrijving')
