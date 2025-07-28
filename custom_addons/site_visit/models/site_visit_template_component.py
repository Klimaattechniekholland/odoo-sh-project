# models.py
from odoo import api, fields, models
from .site_visit_breadcrumb_mixin import SiteVisitBreadcrumbMixin


class TemplateComponent(models.Model, SiteVisitBreadcrumbMixin):
	_name = 'site.visit.template.component'
	_description = 'Template Component'
	_order = 'sequence, name'
	
	category_id = fields.Many2one(
		'site.visit.template.category', required = True, string = 'Category', ondelete = 'cascade'
		)
	point_ids = fields.One2many('site.visit.template.point', 'component_id', string = "Points")
	
	name = fields.Char(required = True, default = "!! Please Rename Component !!")
	sequence = fields.Integer(string = "Sequence", default = 1)
	display_code = fields.Char(string = "Code", compute = "_compute_display_code", store = True)
	
	
	def _get_breadcrumb_chain(self):
		return [
			("category_id", "name"),
			("template_id", "name"),
			]
	
	
	def _compute_breadcrumb_html(self):
		super()._compute_breadcrumb_html()
	
	
	def open_component(self):
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.component',
			'res_id': self.id,
			'view_mode': 'form',
			'target': 'current'
			}
	
	
	@api.depends('sequence', 'category_id.sequence')
	def _compute_display_code(self):
		for rec in self:
			if rec.category_id:
				rec.display_code = f"{rec.category_id.sequence}.{rec.sequence}"
	
	
	def open_copy_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Copy Component',
			'res_model': 'site.visit.template.transient.component',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_component_id': self.id},
			}
	
	
	def resequence_components(self):
		for category in self.mapped('category_id'):
			components = self.search([('category_id', '=', category.id)], order = 'sequence')
			for i, comp in enumerate(components, start = 1):
				comp.sequence = i
	
	
	def write(self, vals):
		res = super().write(vals)
		if 'sequence' not in vals:
			self.resequence_components()
		return res
	
	
	def copy_to_category(self, target_category_id, include_points = True):
		existing_components = self.env['site.visit.template.component'].search(
			[
				('category_id', '=', target_category_id)
				]
			)
		max_seq = max(existing_components.mapped('sequence'), default = 0)
		
		new_component = self.copy(
			{
				'category_id': target_category_id,
				'sequence': max_seq + 1
				}
			)
		
		if include_points:
			for point in self.point_ids:
				point.copy_to_component(new_component.id, include_inputs = True)
		
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.component',
			'res_id': new_component.id,
			'view_mode': 'form',
			'target': 'current',
			}
	
	
	def copy(self, default = None):
		default = dict(default or {})
		siblings = self.search([('category_id', '=', self.category_id.id)])
		next_seq = max(siblings.mapped('sequence'), default = 0) + 1
		default.setdefault('sequence', next_seq)
		new_component = super().copy(default)
		for point in self.point_ids:
			point.copy({'component_id': new_component.id})
		return new_component
