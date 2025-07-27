# models.py
from odoo import models, fields, api


class TemplateTransientComponent(models.TransientModel):
	_name = 'site.visit.template.transient.component'
	_description = 'Template Transient Component'
	
	
	component_id = fields.Many2one("site.visit.template.component", required = True)
	target_category_id = fields.Many2one("site.visit.template.category", required = True)
	include_points = fields.Boolean(default = True)
	
	
	def action_copy_component(self):
		self.ensure_one()
		self.component_id.copy_to_category(self.target_category_id.id, self.include_points)