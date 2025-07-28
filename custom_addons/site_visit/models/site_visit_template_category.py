# models.py
from odoo import api, fields, models
from .site_visit_breadcrumb_mixin import SiteVisitBreadcrumbMixin


class TemplateCategory(models.Model, SiteVisitBreadcrumbMixin):
	_name = 'site.visit.template.category'
	_description = 'Template Category'
	_order = 'sequence, name'
	
	template_id = fields.Many2one('site.visit.template', required = True, ondelete = 'cascade')
	component_ids = fields.One2many('site.visit.template.component', 'category_id', string = "Components")
	
	name = fields.Char( default = "!! Please Rename Category !!", required = True)
	sequence = fields.Integer(string = "Sequence", default = 1)
	display_code = fields.Char(string = "Code", compute = "_compute_display_code", store = True)
	
	def _get_breadcrumb_chain(self):
		return [
			("template_id", "name"),
			]
	
	@api.depends('template_id.name', 'name')
	def _compute_breadcrumb_html(self):
		super()._compute_breadcrumb_html()
	
	
	def open_category(self):
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.category',
			'res_id': self.id,
			'view_mode': 'form',
			'target': 'current'
			}
	
	
	@api.depends('sequence', 'template_id.sequence')
	def _compute_display_code(self):
		for rec in self:
			if rec.template_id:
				rec.display_code = f"{rec.sequence}"
	
	
	def open_copy_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Copy Category',
			'res_model': 'site.visit.template.transient.category',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_category_id': self.id},
			}
	
	
	def resequence_categories(self):
		for template in self.mapped('template_id'):
			cats = self.search([('template_id', '=', template.id)], order = 'sequence')
			for i, cat in enumerate(cats, start = 1):
				cat.sequence = i
	
	
	def write(self, vals):
		res = super().write(vals)
		if 'sequence' not in vals:
			self.resequence_categories()
		return res
	
	
	def copy_to_template(self, target_template_id, include_components = True):
		existing_cats = self.env['site.visit.template.category'].search(
			[
				('template_id', '=', target_template_id)
				]
			)
		max_seq = max(existing_cats.mapped('sequence'), default = 0)
		
		new_category = self.copy(
			{
				'template_id': target_template_id,
				'sequence': max_seq + 1
				}
			)
		
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template.category',
			'res_id': new_category.id,
			'view_mode': 'form',
			'target': 'current',
			}
	
	
	def copy(self, default = None):
		default = dict(default or {})
		siblings = self.search([('template_id', '=', self.template_id.id)])
		next_seq = max(siblings.mapped('sequence'), default = 0) + 1
		default.setdefault('sequence', next_seq)
		new_category = super().copy(default)
		for comp in self.component_ids:
			comp.copy({'category_id': new_category.id})
		return new_category
