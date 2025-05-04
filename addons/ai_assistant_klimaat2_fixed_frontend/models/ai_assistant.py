from odoo import models, fields

class AIAssistant(models.Model):
    _name = 'ai.assistant'
    _description = 'AI Developer Assistant'

    name = fields.Char(string='Name')
    prompt = fields.Text(string='Prompt')
    result = fields.Text(string='Result')