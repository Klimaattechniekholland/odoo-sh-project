# models.py
from odoo import models, fields, api


class TemplateComponent(models.Model):
    _name = 'site.visit.template.component'
    _description = 'Template Component'

    name = fields.Char(required=True)
    category_id = fields.Many2one('site.visit.template.category', required=True, string='Category')
    point_ids = fields.One2many('site.visit.template.point', 'component_id', string="Points")
    sequence = fields.Integer(string="Sequence", default=10)
