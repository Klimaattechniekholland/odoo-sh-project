import logging

from odoo import _, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
_logger.warning("📢 Registering SiteVisit")


class SiteVisit(models.Model):
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_name = 'site.visit'
	_description = 'Site Visit'
	
	customer_id = fields.Many2one('res.partner', string = 'Customer', required = True)
	technician_id = fields.Many2one('res.users', string = 'Technician')
	template_id = fields.Many2one('site.visit.template', string = 'Template')
	image_ids = fields.One2many('site.visit.image', 'visit_id', string = 'Images')
	category_ids = fields.One2many('site.visit.category', 'visit_id', string = 'Categories')
	
	name = fields.Char(
		string = 'Visit Reference', required = True,
		default = lambda self: self.env['ir.sequence'].next_by_code('site.visit')
		)
	visit_date = fields.Date(track_visibility = 'onchange', string = 'Visit Date', default = fields.Date.today)
	
	
	# visit_date = fields.Date(string='Visit Date')
	
	def action_generate_inspection(self):
		if not self.template_id:
			raise UserError(_('Please select an inspection template.'))
		
		with self.env.cr.savepoint():
			for category in self.template_id.category_ids:
				cat = self.env['site.visit.category'].with_context(bypass_restrictions = True).create(
					{
						'name': category.name,
						'visit_id': self.id,
						}
					)
				
				for component in category.component_ids:
					comp = self.env['site.visit.component'].with_context(bypass_restrictions = True).create(
						{
							'name': component.name,
							'category_id': cat.id,
							}
						)
					
					for point_template in component.point_ids:
						point = self.env['site.visit.point'].with_context(bypass_restrictions = True).create(
							{
								'name': point_template.name,
								'component_id': comp.id,
								}
							)
						
						for input_def in point_template.input_ids:
							self.env['site.visit.point.input'].with_context(bypass_restrictions = True).create(
								{
									'point_id': point.id,
									'name': input_def.name,
									'field_type': input_def.field_type,
									}
								)
	
	
	def action_view_images_by_category(self, category):
		return {
			'type': 'ir.actions.act_window',
			'name': f'{category.capitalize()} Photos',
			'res_model': 'site.visit.image',
			'view_mode': 'kanban,tree,form',
			'domain': [('visit_id', '=', self.id), ('category', '=', category)],
			'context': {'default_visit_id': self.id, 'default_category': category}
			}
	
	
	def action_send_report_email(self):
		template = self.env.ref('site_visit.email_template_site_visit')
		for visit in self:
			template.send_mail(visit.id, force_send = True)
