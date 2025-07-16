from odoo import models, fields


class SiteVisitInspectionCategory(models.Model):
    _name = 'site.visit.inspection.category'
    _description = 'Site Visit Inspection Category'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
