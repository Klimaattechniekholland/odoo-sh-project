from odoo import _, api, fields, models


# DRY constants
EP_API_DEFAULT_URL = "https://public.ep-online.nl/api/v5/PandEnergielabel"
BAG_API_DEFAULT_URL = "https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2"
ZIP_API_DEFAULT_URL = "https://openpostcode.nl/api/address"


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'
	
	# zip_api_url = fields.Char(
	# 	string = _("Open ZIP API URL"),
	# 	config_parameter = "bag_ep_api.zip_api_url",
	# 	default = ZIP_API_DEFAULT_URL,
	# 	company_dependent = True
	# 	)
	
	# bag_api_url = fields.Char(
	# 	string = _("BAG API URL"),
	# 	config_parameter = "bag_ep_api.bag_api_url",
	# 	default = BAG_API_DEFAULT_URL,
	# 	company_dependent = True
	# 	)
	
	bag_api_key = fields.Char(
		string = _("BAG API KEY"),
		config_parameter = "bag_ep_api.bag_api_key",
		company_dependent = True
		)
	
	bag_api_exact_match = fields.Boolean(
		string = _("BAG API Exact Match"),
		config_parameter = "bag_ep_api.bag_api_exact_match",
		default = False,
		company_dependent = True
		)
	
	# ep_api_url = fields.Char(
	# 	string = _("EP API URL"),
	# 	config_parameter = "bag_ep_api.ep_api_url",
	# 	default = EP_API_DEFAULT_URL,
	# 	company_dependent = True
	# 	)
	
	ep_api_key = fields.Char(
		string = _("EP API KEY"),
		config_parameter = "bag_ep_api.ep_api_key",
		default = "",
		company_dependent = True
		)
	
	ep_api_recreate = fields.Boolean(
		string = _("EP API Recreate"),
		config_parameter = "bag_ep_api.ep_api_recreate",
		default = False,
		company_dependent = True
		)
	
	ep_api_show_warnings = fields.Boolean(
		string = _("EP API Show Warnings"),
		config_parameter = "bag_ep_api.ep_api_show_warnings",
		default = False,
		company_dependent = True
		)
	
	
	@api.model
	def get_values(self):
		res = super().get_values()
		params = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id)
		res.update(
			{
				# 'zip_api_url': params.get_param('bag_ep_api.zip_api_url', default = ZIP_API_DEFAULT_URL),
				# 'bag_api_url': params.get_param('bag_ep_api.bag_api_url', default = BAG_API_DEFAULT_URL),
				'bag_api_key': params.get_param('bag_ep_api.bag_api_key', default = ''),
				'bag_api_exact_match': params.get_param('bag_ep_api.bag_api_exact_match', default = 'False') == 'True',
				# 'ep_api_url': params.get_param('bag_ep_api.ep_api_url', default = EP_API_DEFAULT_URL),
				'ep_api_key': params.get_param('bag_ep_api.ep_api_key', default = ''),
				'ep_api_recreate': params.get_param('bag_ep_api.ep_api_recreate', default = 'False') == 'True',
				'ep_api_show_warnings': params.get_param(
					'bag_ep_api.ep_api_show_warnings', default = 'False'
					) == 'True',
				# 'ep_api_level_warnings': params.get_param('bag_ep_api.ep_api_level_warnings', default = 'medium')
				}
			)
		return res
	
	
	def set_values(self):
		super().set_values()
		params = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id)
		# params.set_param('bag_ep_api.zip_api_url', self.zip_api_url or '')
		# params.set_param('bag_ep_api.bag_api_url', self.bag_api_url or '')
		params.set_param('bag_ep_api.bag_api_key', self.bag_api_key or '')
		params.set_param('bag_ep_api.bag_api_exact_match', 'True' if self.bag_api_exact_match else 'False')
		
		# params.set_param('bag_ep_api.ep_api_url', self.ep_api_url or '')
		params.set_param('bag_ep_api.ep_api_key', self.ep_api_key or '')
		params.set_param('bag_ep_api.ep_api_recreate', 'True' if self.ep_api_recreate else 'False')
		params.set_param('bag_ep_api.ep_api_show_warnings', 'True' if self.ep_api_show_warnings else 'False')
	# params.set_param('bag_ep_api.ep_api_level_warnings', self.ep_api_level_warnings or 'medium')

# params.set_param('bag_ep_api.max_retries', str(self.max_retries))
# params.set_param('bag_ep_api.retry_delay', str(self.retry_delay))

# @api.constrains('max_retries', 'retry_delay')
# def _check_positive_integers(self):
#     for rec in self:
#         if rec.max_retries < 0:
#             raise ValidationError(_("Max Retries must be a non-negative integer."))
#         if rec.retry_delay < 0:
#             raise ValidationError(_("Retry Delay must be a non-negative integer."))

# @api.constrains('bag_api_url', 'zip_api_url', 'ep_api_url')
# def _check_valid_urls(self):
# 	for rec in self:
# 		for field_name in ['bag_api_url', 'zip_api_url', 'ep_api_url']:
# 			url = rec[field_name]
# 			if url and not url.startswith('https://'):
# 				raise ValidationError(
# 					_("%s must start with https://") % rec._fields[field_name].string
# 					)

# @api.onchange('max_retries', 'retry_delay')
# def _onchange_warn_invalid_retries(self):
#     if self.max_retries < 0 or self.retry_delay < 0:
#         return {
#             'warning': {
#                 'title': _("Invalid Input"),
#                 'message': _("Retry settings should be non-negative."),
#             }
#         }
#     return None
