import logging
import re

from odoo import _, api, fields, models
from odoo.addons.bag_ep_api.services.api_calls.base_resolver import BaseEpResolver
from odoo.addons.bag_ep_api.services.api_calls.resolver_manager import ResolverManager
from odoo.addons.bag_ep_api.utils.buffer_manager import BufferManager
from odoo.addons.bag_ep_api.utils.filter_model_fields import filter_model_fields
from odoo.exceptions import ValidationError
from ..utils.format_dutch_zip import format_dutch_zip


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
	_inherit = 'res.partner'
	
	full_house_number = fields.Char(string = 'Full Number', required = True, translate = True)
	
	house_number = fields.Integer(string = 'Number', readonly = True)
	house_letter = fields.Char(string = 'Letter', size = 1, readonly = True)
	house_number_addition = fields.Integer(string = 'Addition', readonly = True)
	
	addressable_object = fields.Char(string = "Addressable Object", readonly = True)
	
	ep_lookup_status = fields.Integer(
		string = "EP Lookup status",
		tracking = True,
		readonly = True,
		default = 0
		)
	# 0 | not found
	# 1 | ZIP found
	# 2 | BAG found
	# 3 | EP-Online found
	
	ep_data_ids = fields.One2many(
		'ep.data',  # target model
		'partner_id',  # inverse field in ep.data
		store = True,
		)
	
	
	@api.model_create_multi
	def create(self, vals_list):
		partners = super().create(vals_list)
		
		warnings = []
		
		for partner in partners:
			
			fetched_data, warnings = ResolverManager(self).resolve_bag_ep(warnings)
			parsed = fetched_data
			
			if parsed and not partner.parent_id:
				filtered_vals = filter_model_fields(self.env, 'ep.data', parsed.model_dump())
				ep_data_model = self.env['ep.data']
				ep_data_model.create(
					{
						'partner_id': partner.id,
						**filtered_vals
						}
					)
		
		return partners
	
	
	def write(self, vals):
		
		buffer = BufferManager.get(self.env.user.id)
		
		for key in buffer:
			if key not in vals:
				vals[key] = buffer[key]
		
		res = super().write(vals)
		
		return res
	
	
	@api.onchange('country_id')
	def _onchange_country_id_refresh_states(self):
		if self.country_id:
			# If exactly 1 state is available, pre-fill it
			states = self.env['res.country.state'].search([('country_id', '=', self.country_id.id)])
			self.state_id = states[0] if len(states) == 1 else False
		else:
			self.state_id = False
	
	
	@api.onchange('zip')
	def _onchange_zip(self):
		warnings = []
		for record in self:
			# record.ep_lookup_status = 0
			# BufferManager.set(self.env.user.id,'ep_lookup_status', 0)
			
			if record.zip:
				formatted = format_dutch_zip(record.zip)
				
				if formatted:
					record.zip = formatted
				
				else:
					record.street = ''
					record.city = ''
					record.state_id = False
					
					warnings.add(
						"warning", _("ZIP -- Invalid ZIP Code: '%(zip)s'. Please use format '1234 AB' or '1234AB'.") % {
							'zip': record.zip
							}
						)
			
			if not warnings:
				if record.parent_id:
					fetched_data, warnings = ResolverManager(self).resolve_zip(warnings, True)
				else:
					fetched_data, warnings = ResolverManager(self).resolve_all(warnings, True)
				
				return self._handle_onchange_result(
					warnings = warnings,
					model_name = 'ep.data',
					data_model = fetched_data,
					ep_lookup_status = self.ep_lookup_status,
					)
		
		return None
	
	
	# When saved, if is changed. And when create or write.
	# If error, the save/writing will be aborted.
	@api.constrains('full_house_number')
	def _check_code_format_full_house_number(self):
		for record in self:
			if record.full_house_number:
				match = re.match(r"^(\d+)([A-Za-z]?)(?:-(\d+))?$", record.full_house_number.strip())
				if not match:
					raise ValidationError(_("Invalid house number format: %s") % record.full_house_number)
	
	
	@api.constrains('zip')
	def _check_code_format_zip(self):
		for record in self:
			if record.zip:
				match = re.match(r"^(\d{4})([A-Z]{2})$", record.zip.replace(" ", "").upper())
				if not match:
					raise ValidationError(_("Invalid zip: %s") % record.zip)
	
	
	@api.onchange('full_house_number')
	def _onchange_full_house_number(self):
		warnings = []
		fetched_data = None
		for partner in self:
			
			if not warnings:
				if partner.parent_id:
					fetched_data, warnings = ResolverManager(self).resolve_zip(warnings, True)
				else:
					fetched_data, warnings = ResolverManager(self).resolve_all(warnings, True)
			
			return self._handle_onchange_result(
				warnings = warnings,
				model_name = 'ep.data',
				data_model = fetched_data,
				ep_lookup_status = self.ep_lookup_status,
				)
		
		return None
	
	
	@api.onchange('street')
	def _onchange_street(self):
		# warnings = []
		for record in self:
			record.ep_lookup_status = 0
			if record.street:
				# This regex looks for something like 70, 70A, 70-1, or 70A-1 at the end
				match = re.search(r"(\d+)([A-Za-z]?)(?:-(\d+))?$", record.street.strip())
				
				if match:
					number = match.group(1)  # e.g., '70'
					letter = match.group(2) or ''  # e.g., 'A' or ''
					addition = match.group(3) or ''  # e.g., '1' or ''
					if str(number).strip().lower() != str(record.house_number).strip().lower() \
							or str(letter).strip().lower() != str(record.house_letter).strip().lower() \
							or str(addition).strip().lower() != str(record.house_number_addition).strip().lower():
						
						# Construct full_house_number with conditional hyphen
						if addition:
							full_number = f"{number}{letter}-{addition}"
						else:
							full_number = f"{number}{letter}"
						
						record.full_house_number = full_number
				# this will trigger the onchange for full_house_number
	
	
	def _handle_onchange_result(self, warnings = None, model_name = None, data_model = None, ep_lookup_status = None):
		#
		# Optionally recreate One2many values from buffer.
		# This will display directly the information without pressing the "write" button.
		# Side effect is that we delete first the references and then create a new one record with the reference
		# Need to set the delete to cascade then there will be no records with empty partner_id.
		#
		result = {}
		# delete ep.data records linked to the partner - self
		self.ep_data_ids = [(6, 0, [])]
		
		if self._get_recreate() and data_model and model_name and ep_lookup_status > 1:
			parsed = data_model
			
			if parsed:
				filtered_vals = filter_model_fields(self.env, model_name, parsed.model_dump())
				# create a new ep.data record linked to the partner - self
				self.ep_data_ids = [(0, 0, filtered_vals)]
				result.setdefault('value', {})['ep_data_ids'] = self.ep_data_ids
		
		# Show a warning message if needed
		if warnings and self._get_show_warnings():
			result['warning'] = {
				'title': " -- Warning -- ",
				'message': "\n".join(warnings),
				}
		
		return result or None
	
	
	def _get_recreate(self):
		api_recreate = self.env['ir.config_parameter'].sudo().with_context(
			company_id = self.env.company.id
			).get_param(
			'bag_ep_api.ep_api_recreate', default = ''
			).strip().lower() or False
		return api_recreate == 'true'
	
	
	def _get_show_warnings(self):
		api_show_warnings = self.env['ir.config_parameter'].sudo().with_context(
			company_id = self.env.company.id
			).get_param(
			'bag_ep_api.ep_api_show_warnings', default = ''
			).strip().lower() or False
		
		return api_show_warnings == 'true'
	
	
	def _get_level_warnings(self):
		api_level_warnings = self.env['ir.config_parameter'].sudo().with_context(
			company_id = self.env.company.id
			).get_param(
			'bag_ep_api.ep_api_level_warnings', default = 'none'
			).strip().lower() or False
		return api_level_warnings == 'true'
	
	
	def action_reset_to_defaults(self):
		exclude_fields = {'id', 'create_uid', 'create_date', 'write_uid', 'write_date'}
		field_names = [f for f in self.fields_get().keys() if f not in exclude_fields]
		
		for record in self:
			defaults = record.default_get(field_names)
			record.write(defaults)
	
	
	def action_ep_api_lookup(self):
		"""Manual BAG fetch from the UI button, and clear Caches and BufferManager"""
		
		warnings = []
		BufferManager.clear(self.env.user.id)
		BaseEpResolver.clear_partner_cache_static(self, self.env)
		
		for partner in self:
			parsed, warnings = ResolverManager(self).resolve_all(warnings, True)
			
			if parsed:
				filtered_vals = filter_model_fields(self.env, 'ep.data', parsed.model_dump())
				ep_data_model = self.env['ep.data']
				
				existing = ep_data_model.search([('partner_id', '=', partner.id)], limit = 1)
				
				if existing:
					existing.write(filtered_vals)
				else:
					filtered_vals['partner_id'] = partner.id
					ep_data_model.create(filtered_vals)
