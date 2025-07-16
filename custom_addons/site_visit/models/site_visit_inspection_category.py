from odoo import models, fields

import logging
_logger = logging.getLogger(__name__)
_logger.warning("📢 Registering SiteVisitInspectionCategory")


class SiteVisitInspectionCategory(models.Model):
    _name = 'site.visit.inspection.category'
    _description = 'Site Visit Inspection Category'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
