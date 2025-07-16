from odoo import models, fields

class SiteVisitInspectionComponent(models.Model):
    _name = 'site.visit.inspection.component'
    _description = 'Site Visit Component'

    category_id = fields.Many2one('site.visit.inspection.category', string='Category', required=True)
    
    name = fields.Char(string='Component Name', required=True)
    description = fields.Char(string='Description', required=True)
    
