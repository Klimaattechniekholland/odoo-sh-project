from odoo import models, fields, api

class ExampleModel(models.Model):
    _name = 'ai.assistant.example'
    _description = 'Voorbeeldmodel voor AI Assistent'

    name = fields.Char(string="Naam")
