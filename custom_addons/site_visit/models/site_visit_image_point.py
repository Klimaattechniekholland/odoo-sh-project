from odoo import models, fields

class SiteVisitImagePoint(models.Model):
    _name = 'site.visit.image.point'
    _description = 'Site Visit Inspection Point'

    image_id = fields.Many2one('site.visit.image', string='System Photo', required=True, ondelete='cascade')
    template_id = fields.Many2one('site.visit.inspection.point', string='Checklist Item', required=True)
    photo = fields.Binary(string='Photo', attachment=True)
    note = fields.Text(string='Details / Observation')