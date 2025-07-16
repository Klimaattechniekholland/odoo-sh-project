from odoo import models, fields


import logging
_logger = logging.getLogger(__name__)
_logger.warning("📢 Registering SiteVisitInspectionPoint")



class SiteVisitInspectionPoint(models.Model):
    _name = 'site.visit.inspection.point'
    _description = 'Site Visit Inspection Point'

    category_id = fields.Many2one('site.visit.inspection.category', string='Main Category', required=True)
    component_id = fields.Many2one('site.visit.inspection.component', string='Component')
    
    name = fields.Char(string='Checklist Item', required=True)
    description = fields.Char(string='Description Item', required=True)
