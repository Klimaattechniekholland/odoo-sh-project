# models.py
from odoo import models, fields, api

class TemplateTransientCategory(models.TransientModel):
	_name = 'site.visit.template.transient.category'
	_description = 'Template Transient Category'
	
	
	category_id = fields.Many2one("site.visit.template.category", required = True)
	target_template_id = fields.Many2one("site.visit.template", required = True)
	include_components = fields.Boolean(default = True)
	
	
	def action_copy_category(self):
		self.ensure_one()
		self.category_id.copy_to_template(self.target_template_id.id, self.include_components)

