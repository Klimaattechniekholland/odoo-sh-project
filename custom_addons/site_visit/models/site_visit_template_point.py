# models.py
from odoo import api, fields, models


class TemplatePoint(models.Model):
	_name = 'site.visit.template.point'
	_description = 'Template Point'
	_order = 'sequence, name'
	
	component_id = fields.Many2one('site.visit.template.component', required = True, ondelete = 'cascade')
	input_ids = fields.One2many('site.visit.template.input', 'point_id', string = 'Inputs')
	
	name = fields.Char(required = True)
	sequence = fields.Integer(string = "Sequence", default = 1)
	display_code = fields.Char(string = "Code", compute = "_compute_display_code", store = True)
	
	input_count = fields.Integer(
		string = 'Input Count',
		compute = '_compute_input_count',
		store = True
		)
	
	breadcrumb_html = fields.Html(string = "Breadcrumb", compute = "_compute_breadcrumb_html")
	
	@api.depends(
		'component_id.name', 'component_id.category_id.name', 'component_id.category_id.template_id.name', 'name'
		)
	def _compute_breadcrumb_html(self):
		for rec in self:
			comp = rec.component_id
			cat = comp.category_id
			tmpl = cat.template_id
			rec.breadcrumb_html = (
				f'<a href="#" class="o_breadcrumb_link" data-model="site.visit.template" data-id="{tmpl.id}">{tmpl.name}</a>'
				f' &raquo; <a href="#" class="o_breadcrumb_link" data-model="site.visit.template.category" data-id="{cat.id}">{cat.name}</a>'
				f' &raquo; <a href="#" class="o_breadcrumb_link" data-model="site.visit.template.component" data-id="{comp.id}">{comp.name}</a>'
				f' &raquo; <a href="#" class="o_breadcrumb_link" data-model="site.visit.template.point" data-id="{rec.id}">{rec.name}</a>'
			)
	
	
	def open_point(self):
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.point',
			'res_id': self.id,
			'view_mode': 'form',
			'target': 'current'
			}
	
	
	@api.depends('input_ids')
	def _compute_input_count(self):
		for point in self:
			point.input_count = len(point.input_ids)
	
	
	@api.depends('sequence', 'component_id.sequence', 'component_id.category_id.sequence')
	def _compute_display_code(self):
		for rec in self:
			if rec.component_id:
				rec.display_code = f"{rec.component_id.display_code}.{rec.sequence}"
	
	
	def open_copy_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Copy Point',
			'res_model': 'site.visit.template.transient.point',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_point_id': self.id},
			}
	
	
	def resequence_points(self):
		for component in self.mapped('component_id'):
			points = self.search([('component_id', '=', component.id)], order = 'sequence')
			for i, pt in enumerate(points, start = 1):
				pt.sequence = i
	
	
	def write(self, vals):
		res = super().write(vals)
		if 'sequence' not in vals:
			self.resequence_points()
		return res
	
	
	def copy_to_component(self, target_component_id, include_inputs = True):
		existing_points = self.env['site.visit.template.point'].search(
			[
				('component_id', '=', target_component_id)
				]
			)
		max_seq = max(existing_points.mapped('sequence'), default = 0)
		
		new_point = self.copy(
			{
				'component_id': target_component_id,
				'sequence': max_seq + 1
				}
			)
		
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.point',
			'res_id': new_point.id,
			'view_mode': 'form',
			'target': 'current',
			}
	
	
	def copy(self, default = None):
		default = dict(default or {})
		siblings = self.search([('component_id', '=', self.component_id.id)])
		next_seq = max(siblings.mapped('sequence'), default = 0) + 1
		default.setdefault('sequence', next_seq)
		new_point = super().copy(default)
		for input_rec in self.input_ids:
			input_rec.copy({'point_id': new_point.id})
		return new_point
