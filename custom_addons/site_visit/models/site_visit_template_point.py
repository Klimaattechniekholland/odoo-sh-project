# models.py
from odoo import models, fields, api


class TemplatePoint(models.Model):
    _name = 'site.visit.template.point'
    _description = 'Template Point'

    name = fields.Char(required=True)
    component_id = fields.Many2one('site.visit.template.component', required=True)
    sequence = fields.Integer(string="Sequence", default=10)
