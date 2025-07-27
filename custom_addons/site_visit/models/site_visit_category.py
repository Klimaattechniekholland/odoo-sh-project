import logging

from odoo import fields, models


_logger = logging.getLogger(__name__)
_logger.warning("📢 Registering SiteVisitCategory")


class SiteVisitCategory(models.Model):
	_name = "site.visit.category"
	_description = 'Site Visit Category'
	_order = 'sequence, name'
	
	name = fields.Char(string = "Name", required = True,  readonly=True)
	description = fields.Text(string = "Description")
	sequence = fields.Integer(default = 10)
	
	visit_id = fields.Many2one('site.visit', string='Site Visit', ondelete='cascade', readonly=True)

	component_ids = fields.One2many("site.visit.component", "category_id", readonly=True)
