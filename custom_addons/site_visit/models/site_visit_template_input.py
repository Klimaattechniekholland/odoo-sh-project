from odoo import api, fields, models
from .site_visit_breadcrumb_mixin import SiteVisitBreadcrumbMixin


class SiteVisitTemplateInput(models.Model, SiteVisitBreadcrumbMixin):
	_name = 'site.visit.template.input'
	_description = 'Template Input Definition'
	_order = 'sequence, name'
	
	point_id = fields.Many2one(
		'site.visit.template.point',
		string = 'Template Point',
		required = True,
		ondelete = 'cascade'
		)
	
	name = fields.Char(string = "Label", default = "!! Please Rename Input !!", required = True)
	description = fields.Char(string = "Description", required = True)
	display_code = fields.Char(string = "Code", compute = "_compute_display_code", store = True)
	sequence = fields.Integer(string = "Sequence", default = 1)
	
	field_type = fields.Selection(
		[
			('char', 'Text'),
			('int', 'Integer'),
			('float', 'Float'),
			('bool', 'Checkbox'),
			('image', 'Image'),
			('text', 'Note'),
			], string = "Field Type", required = True
		)
		
	
	def _get_breadcrumb_chain(self):
		return [
			("point_id", "name"),
			("component_id", "name"),
			("category_id", "name"),
			("template_id", "name"),
			]
	
	
	@api.depends(
		'point_id.name', 'point_id.component_id.name', 'point_id.component_id.category_id.name',
		'point_id.component_id.category_id.template_id.name', 'name'
		)
	def _compute_breadcrumb_html(self):
		super()._compute_breadcrumb_html()
	
	
	def open_input(self):
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.input',
			'res_id': self.id,
			'view_mode': 'form',
			'target': 'current'
			}


	@api.depends(
		'sequence', 'point_id.sequence', 'point_id.component_id.sequence', 'point_id.component_id.category_id.sequence'
		)
	def _compute_display_code(self):
		for rec in self:
			if rec.point_id and rec.point_id.component_id and rec.point_id.component_id.category_id:
				rec.display_code = (
					f"{rec.point_id.component_id.category_id.sequence}"
					f".{rec.point_id.component_id.sequence}"
					f".{rec.point_id.sequence}"
					f".{rec.sequence}"
				)
	
	
	def open_copy_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Copy Input',
			'res_model': 'site.visit.template.transient.input',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_input_id': self.id},
			}
	
	
	def resequence_inputs(self):
		for point in self.mapped('point_id'):
			inputs = self.search([('point_id', '=', point.id)], order = 'sequence')
			for i, inp in enumerate(inputs, start = 1):
				inp.sequence = i
	
	
	def write(self, vals):
		res = super().write(vals)
		if 'sequence' not in vals:
			self.resequence_inputs()
		return res
	
	
	def copy_to_point(self, target_point_id):
		existing_inputs = self.search([('point_id', '=', target_point_id)])
		max_seq = max(existing_inputs.mapped('sequence'), default = 0)
		new_input = self.copy(
			{
				'point_id': target_point_id,
				'sequence': max_seq + 1
				}
			)
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.input',
			'res_id': new_input.id,
			'view_mode': 'form',
			'target': 'current',
			}
	
	
	def copy(self, default = None):
		default = dict(default or {})
		siblings = self.search([('point_id', '=', self.point_id.id)])
		next_seq = max(siblings.mapped('sequence'), default = 0) + 1
		default.setdefault('sequence', next_seq)
		return super().copy(default)
