# models.py
from odoo import fields, models, api


class TemplateTransientPoint(models.TransientModel):
	_name = 'site.visit.template.transient.point'
	_description = 'Template Transient Point'
	
	point_id = fields.Many2one("site.visit.template.point", required = True)
	target_component_id = fields.Many2one("site.visit.template.component", required = True)
	include_inputs = fields.Boolean(default = True)
	
	
	def action_copy_point(self):
		self.ensure_one()
		self.point_id.copy_to_component(self.target_component_id.id, self.include_inputs)

