# models.py
from odoo import api, fields, models
from .site_visit_breadcrumb_mixin import SiteVisitBreadcrumbMixin


class Template(models.Model, SiteVisitBreadcrumbMixin):
	_name = 'site.visit.template'
	_description = 'Configuration Template'
	_order = 'sequence, name'
	
	name = fields.Char( default = "!! Please Rename Template !!", required = True)
	category_ids = fields.One2many('site.visit.template.category', 'template_id', string = 'Categories')
	sequence = fields.Integer(string = "Sequence", default = 10)
	breadcrumb_html = fields.Html(string = "Breadcrumb", compute = "_compute_breadcrumb_html")
	
	
	def _get_breadcrumb_chain(self):
		return [
			("template_id", "name"),
			]
	
	
	@api.depends('name')
	def _compute_breadcrumb_html(self):
		super()._compute_breadcrumb_html()
	
	
	def open_template(self):
		return {
			'type': 'ir.actions.act_window',
			'res_model': 'site.visit.template',
			'res_id': self.id,
			'view_mode': 'form',
			'target': 'current'
			}
	
	
	def copy(self, default = None):
		default = dict(default or {})
		default.setdefault('name', f"{self.name} (copy)")
		new_template = super().copy(default)
		
		for category in self.category_ids:
			category.copy({'template_id': new_template.id})
		
		return new_template
	
	
	def copy_to_new(self, include_structure = True):
		new_template = self.copy({'name': f"{self.name} (copy)"})
		if include_structure:
			for category in self.category_ids:
				new_cat = category.copy({'template_id': new_template.id})
				for component in category.component_ids:
					new_comp = component.copy({'category_id': new_cat.id})
					for point in component.point_ids:
						new_point = point.copy({'component_id': new_comp.id})
						for input_field in point.input_ids:
							input_field.copy({'point_id': new_point.id})
		return new_template
	
	
	def open_copy_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Copy Template',
			'res_model': 'site.visit.template.transient',
			'view_mode': 'form',
			'target': 'new',
			'context': {'default_template_id': self.id},
			}
	
	
	def resequence_all(self):
		for template in self:
			template.category_ids.resequence_categories()
			for category in template.category_ids:
				category.component_ids.resequence_components()
				for component in category.component_ids:
					component.point_ids.resequence_points()
					for point in component.point_ids:
						point.input_ids.resequence_inputs()
	
	
	def button_resequence_all(self):
		self.resequence_all()
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
			}
