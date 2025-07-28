
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'
	
	sales5_client_id = fields.Char(
		related = 'company_id.sales5_client_id', string = "Sales5 Client ID", readonly = False
		)
	sales5_client_secret = fields.Char(
		related = 'company_id.sales5_client_secret', string = "Sales5 Client Secret", readonly = False
		)
	
	
	def set_values(self):
		super().set_values()
		self.env['ir.config_parameter'].sudo().set_param('sales5.api.client_id', self.sales5_client_id)
		self.env['ir.config_parameter'].sudo().set_param('sales5.api.client_secret', self.sales5_client_secret)
	
	
	def get_values(self):
		res = super().get_values()
		params = self.env['ir.config_parameter'].sudo()
		res.update(
			{
				'sales5_client_id': params.get_param('sales5.api.client_id'),
				'sales5_client_secret': params.get_param('sales5.api.client_secret'),
				}
			)
		return res