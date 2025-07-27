# models.py
from odoo import models, fields, api
from odoo.exceptions import UserError


class TemplateTransient(models.TransientModel):
	_name = 'site.visit.template.transient'
	_description = 'Configuration Template Transient'
	
	template_id = fields.Many2one("site.visit.template", required = True)
	include_structure = fields.Boolean(default = True)
	
	
	def action_copy_template(self):
		self.ensure_one()
		self.template_id.copy_to_new(self.include_structure)
	