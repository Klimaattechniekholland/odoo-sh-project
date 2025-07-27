import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
_logger.warning("📢 Registering SiteVisitPoint")


class SiteVisitPoint(models.Model):
	_name = 'site.visit.point'
	_description = 'Site Visit Point'
	_order = 'sequence, name'
	
	# category_id = fields.Many2one('site.visit.category', string = 'Main Category', required = True)
	component_id = fields.Many2one('site.visit.component', string = 'Component', ondelete = 'cascade')
	input_ids = fields.One2many('site.visit.point.input', 'point_id', string = 'Inputs')
	
	name = fields.Char(string = 'Checklist Item', required = True)
	description = fields.Char(string = 'Description Item')
	sequence = fields.Integer(default = 10)
	
	
	@api.model
	def create(self, vals):
		if self.env.context.get('bypass_restrictions'):
			return super().create(vals)
		raise UserError(_('You cannot create points manually during the inspection.'))
	
	
	def unlink(self):
		if self.env.context.get('bypass_restrictions'):
			return super().unlink()
		raise UserError(_('You cannot delete points during the inspection.'))
