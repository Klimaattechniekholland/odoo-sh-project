# models.py
from odoo import models, fields, api

class Installation(models.Model):
    _name = 'site.visit.installation'
    _description = 'User Installation Record'

    name = fields.Char()
    template_id = fields.Many2one('site.visit.template', required=True)
    user_category_ids = fields.One2many('site.visit.user.category', 'installation_id')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.user_category_ids = [(5, 0, 0)]
            for template_cat in self.template_id.category_ids:
                cat_vals = {
                    'template_category_id': template_cat.id,
                    'user_component_ids': []
                }
                for comp in template_cat.component_ids:
                    comp_vals = {
                        'template_component_id': comp.id,
                        'user_point_ids': [
                            (0, 0, {'template_point_id': pt.id}) for pt in comp.point_ids
                        ]
                    }
                    cat_vals['user_component_ids'].append((0, 0, comp_vals))
                self.user_category_ids += [(0, 0, cat_vals)]
