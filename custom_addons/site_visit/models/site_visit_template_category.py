# models.py
from odoo import models, fields, api

class TemplateCategory(models.Model):
    _name = 'site.visit.template.category'
    _description = 'Template Category'

    name = fields.Char(required=True)
    template_id = fields.Many2one('site.visit.template', required=True)
    component_ids = fields.One2many('site.visit.template.component', 'category_id', string="Components")
    sequence = fields.Integer(string="Sequence", default=10)
