# models.py
from odoo import models, fields, api



class UserComponent(models.Model):
    _name = 'site.visit.user.component'

    user_category_id = fields.Many2one('site.visit.user.category')
    template_component_id = fields.Many2one('site.visit.template.component')
    user_point_ids = fields.One2many('site.visit.user.point', 'user_component_id')

