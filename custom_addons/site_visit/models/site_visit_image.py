from odoo import models, fields, api

class SiteVisitImage(models.Model):
    _name = 'site.visit.image'
    _description = 'Site Visit Image'
    
    
    visit_id = fields.Many2one('site.visit', string='Site Visit', required=True, ondelete='cascade')

    category_id = fields.Many2one('site.visit.inspection.category', string='Category')
    component_id = fields.Many2one('site.visit.inspection.component', string='Component')
    point_ids = fields.One2many('site.visit.image.point', 'image_id', string='Sub-Points')
    
    image = fields.Binary(string='Photo', required=True, attachment=True)
    note = fields.Char(string='Note')

    # @api.model
    # def create(self, vals):
    #     record = super().create(vals)
    #     template_items = self.env['site.inspection.point.template'].search([
    #         ('category_id', '=', record.category_id.id),
    #         '|', ('component_id', '=', False), ('component_id', '=', record.component_id.id)
    #     ])
    #     for item in template_items:
    #         self.env['site.visit.image.point'].create({
    #             'image_id': record.id,
    #             'template_id': item.id,
    #         })
    #     return record