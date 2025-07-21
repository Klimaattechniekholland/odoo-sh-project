# models.py
from odoo import models, fields, api


class UserPoint(models.Model):
    _name = 'site.visit.user.point'

    user_component_id = fields.Many2one('site.visit.user.component')
    template_point_id = fields.Many2one('site.visit.template.point')
    value = fields.Char("User Value")
