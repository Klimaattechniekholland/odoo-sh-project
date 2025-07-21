# models.py
from odoo import models, fields, api

class Template(models.Model):
    _name = 'site.visit.template'
    _description = 'Configuration Template'

    name = fields.Char(required=True)
    category_ids = fields.One2many('site.visit.template.category', 'template_id')
    sequence = fields.Integer(string="Sequence", default=10)
