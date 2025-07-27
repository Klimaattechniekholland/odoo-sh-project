from odoo import fields, models


class SiteVisitInspection(models.Model):
    _name = "site.visit.inspection"
    _description = "Site Visit Inspection"
    
    name = fields.Char(string = "Name", required = True)
    description = fields.Text(string = "Description")
    
    category_ids = fields.One2many("site.visit.category", "visit_id")