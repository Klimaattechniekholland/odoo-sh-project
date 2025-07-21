# models.py
from odoo import models, fields, api


class UserCategory(models.Model):
    _name = 'site.visit.user.category'

    installation_id = fields.Many2one('site.visit.installation')
    template_category_id = fields.Many2one('site.visit.template.category')
    user_component_ids = fields.One2many('site.visit.user.component', 'user_category_id')
