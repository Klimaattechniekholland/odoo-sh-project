from odoo import fields, models


class SiteVisitTemplateTransientInput(models.TransientModel):
	_name = 'site.visit.template.transient.input'
	_description = 'Template Transient Input Definition'
	
	input_id = fields.Many2one("site.visit.template.input", required = True)
	target_point_id = fields.Many2one("site.visit.template.point", required = True)
	
	
	def action_copy_input(self):
		self.ensure_one()
		self.input_id.copy_to_point(self.target_point_id.id)