import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
_logger.warning("📢 Registering SiteVisitComponent")


class SiteVisitComponent(models.Model):
	_name = 'site.visit.component'
	_description = 'Site Visit Component'
	_order = 'sequence, name'
	
	category_id = fields.Many2one('site.visit.category', string = 'Category', ondelete = 'cascade', readonly=True)
	point_ids = fields.One2many("site.visit.point", "component_id")
	
	name = fields.Char(string = 'Component Name', required = True, readonly=True)
	description = fields.Char(string = 'Description')
	sequence = fields.Integer(default = 10)
	
	
	@api.model
	def create(self, vals):
		if self.env.context.get('bypass_restrictions'):
			return super().create(vals)
		raise UserError(_('You cannot create components manually during the inspection.'))
	
	
	def unlink(self):
		if self.env.context.get('bypass_restrictions'):
			return super().unlink()
		raise UserError(_('You cannot delete components during the inspection.'))
