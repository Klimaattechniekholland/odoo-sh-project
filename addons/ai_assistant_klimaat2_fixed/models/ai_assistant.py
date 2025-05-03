from odoo import models, fields

class AiAssistant(models.Model):
    _name = 'ai.assistant'
    _description = 'AI Developer Assistant'

    name = fields.Char(string='Naam')
    description = fields.Text(string='Beschrijving')
