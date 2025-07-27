from odoo import fields, models, api, _


class SiteVisitPointInput(models.Model):
	_name = 'site.visit.point.input'
	_description = 'Site Visit Input'
	
	point_id = fields.Many2one('site.visit.point', string = 'Point', ondelete = 'cascade')
	name = fields.Char(string = 'Label', required = True)
	field_type = fields.Selection(
		[
			('char', 'Text'),
			('int', 'Integer'),
			('float', 'Float'),
			('bool', 'Checkbox'),
			('image', 'Image'),
			('text', 'Note'),
			], required = True
		)
	
	value_char = fields.Char(string = 'Text')
	value_integer = fields.Integer("Integer", default = 0)
	value_float = fields.Float(string = 'Decimal')
	value_bool = fields.Boolean(string = "Checkbox")
	value_image = fields.Binary(string = 'Image')
	value_note = fields.Text(string = 'Note')
	
	
	@api.depends('field_type', 'value_char', 'value_float', 'value_integer', 'value_note', 'value_bool', 'value_image')
	def _compute_display_value(self):
		for rec in self:
			rec.display_value = {
				'char': rec.value_char or '',
				'float': str(rec.value_float) if rec.value_float is not None else '',
				'integer': str(rec.value_integer) if rec.value_integer is not None else '',
				'note': rec.value_note or '',
				'bool': '✔' if rec.value_bool else '✘',
				'image': '🖼️' if rec.value_image else '',
				}.get(rec.field_type, '')
	
	
	display_value = fields.Char(compute = '_compute_display_value', string = 'Preview', store = False)
