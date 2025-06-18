from odoo import models, fields, api, _
import logging
import re
from odoo.addons.bag_ep_api.utils.buffer_manager import BufferManager
from odoo.addons.bag_ep_api.utils.filter_model_fields import filter_model_fields
from ..utils.format_dutch_zip import format_dutch_zip
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
	_inherit = 'res.partner'
	
	# get address items from zip and full house number, for the Dutch market,
	# country_id = 165, NL, The Netherlands.
	# to get from the full house number: 70, 70 A, 70-1, 70A-1
	# the number, 70
	# optional letters, an
	# optional extension, -1
	# if the ZipData(BaseModel) is found then fill the fields bag_api for the street and city
	# populates the result data in res.partner table/fields.
	# with the ep-online call, we get all Energy Label information
	# when the square meters or built year are not given by the ep-online
	# use BagApi to get the information.
	# the Zip information is a class (Basemodel), not stored in the database.
	# the EpData information is a class (models.Model) with Many2One reference in res.partner
	# and stored in the database.
	
	#
	# NOTE:
	# do not use the raise User Error it will refill the form with the saved data.
	#
	# self.ep_data_ids = [(5, 0, 0)]
	# self.ep_data_ids += [(0, 0, vals) for vals in filtered_vals]  - multiple records
	# self.ep_data_ids += [(0, 0, filtered_vals)] - one record
	#
	# | Command | Format | Description |
	# | ------- | ----------------- | ---------------------------------------------------------------------------- |
	# | `0`     | `(0, 0, values)`  | Create a new record with the given `values` (dict of field values).|
	# | `1`     | `(1, ID, values)` | Update the record with `ID` using the given `values`.|
	# | `2`     | `(2, ID, 0)`      | Delete the record with `ID`.Only works on `One2many`.|
	# | `3`     | `(3, ID, 0)`      | Unlink the  record with `ID` from the relation, but do not delete it.|
	# | `4`     | `(4, ID, 0)`      | Link to an existing record  with `ID`.Does not create or update.|
	# | `5`     | `(5, 0, 0)`       | Clear all existing records in the relation. | deprecated use (6, 0, [])
	# | `6`     | `(6, 0, [IDs])`   | Replace al existing links with the provided list of IDs.|
	
	full_house_number = fields.Char(string = 'Full Number', required = True, translate = True)
	
	house_number = fields.Integer(string = 'Number', readonly = True)
	house_letter = fields.Char(string = 'Letter', size = 1, readonly = True)
	house_number_addition = fields.Integer(string = 'Addition', readonly = True)
	addressable_object = fields.Char(string = "Addressable Object", readonly = True)
	
	ep_lookup_status = fields.Integer(string = "EP Lookup status", default = 0)
	# 0 | not found
	# 1 | ZIP found
	# 2 | BAG found
	# 3 | EP-Online found
	
	lookup_status = fields.Selection(
		selection = [
			('idle', 'Idle'),
			('success', 'Success'),
			('error', 'Error')
			],
		default = 'idle'
		)
	
	ep_data_ids = fields.One2many(
		'ep.data',  # target model
		'partner_id',  # inverse field in ep.data
		store = True,
		)
	
	
	@api.model_create_multi
	def create(self, vals_list):
		partners = super().create(vals_list)
		for partner in partners:
			parsed = BufferManager.get()
			
			if parsed and not partner.parent_id:
				filtered_vals = filter_model_fields(self.env, 'ep.data', parsed.model_dump())
				ep_data_model = self.env['ep.data']
				ep_data_model.create(
					{
						'partner_id': partner.id,
						**filtered_vals
						}
					)
			BufferManager.clear()
		
		return partners
	
	
	def write(self, vals):
		result = super().write(vals)
		
		for partner in self:
			parsed = BufferManager.get()
			
			if parsed and not partner.parent_id:
				filtered_vals = filter_model_fields(self.env, 'ep.data', parsed.model_dump())
				ep_data_model = self.env['ep.data']
				existing = ep_data_model.search([('partner_id', '=', partner.id)], limit = 1)
				
				if existing:
					existing.write(filtered_vals)
				else:
					ep_data_model.create(
						{
							'partner_id': partner.id,
							**filtered_vals
							}
						)
			BufferManager.clear()
		
		return result
	
	
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
			record.ep_lookup_status = 0
			record.lookup_status = 'idle'
			if not record.zip:
				continue
			formatted = format_dutch_zip(record.zip)
			if formatted:
				record.zip = formatted
			else:
				record.street = ''
				record.city = ''
				record.state_id = False
				
				warnings.append(
					f"ZIP -- Invalid ZIP Code: '{record.zip}' "
					f"Please use format '1234 AB' or '1234AB'.."
					)
		
		if not warnings:
			self._call_api_lookups(warnings)
			
			return self._handle_onchange_result(
				warnings = warnings,
				model_name = 'ep.data',
				buffer_model = BufferManager,
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
		for partner in self:
			partner.ep_lookup_status = 0
			partner._full_house_number_format(warnings)
			
			if not warnings:
				if partner.parent_id:
					self._zip_auto_fill_address_sync(warnings)
				else:
					partner._call_api_lookups(warnings)
			
			return self._handle_onchange_result(
				warnings = warnings,
				model_name = 'ep.data',
				buffer_model = BufferManager,
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
	
	
	def _handle_onchange_result(self, warnings = None, model_name = None, buffer_model = None, ep_lookup_status = None):
		#
		# Optionally recreate One2many values from buffer.
		# This will display directly the information without pressing the "write" button.
		# Side effect is that we delete first the references and then create a new one record with the reference
		# Need to set the delete to cascade then there will be no records with empty partner_id.
		#
		result = {}
		if self._get_recreate() and buffer_model and model_name and ep_lookup_status > 1:
			# delete ep.data records linked to the partner - self
			self.ep_data_ids = [(6, 0, [])]
			parsed = buffer_model.get()
			if parsed:
				filtered_vals = filter_model_fields(self.env, model_name, parsed.model_dump())
				# create a new ep.data record linked to the partner - self
				self.ep_data_ids = [(0, 0, filtered_vals)]
				result.setdefault('value', {})['ep_data_ids'] = self.ep_data_ids
			BufferManager.clear()
		
		# Show a warning message if needed
		if warnings and self._get_show_warnings():
			result['warning'] = {
				'title': " -- Warning -- ",
				'message': "\n".join(warnings),
				}
		
		return result or None
	
	
	def _get_recreate(self):
		api_recreate = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id).get_param(
			'bag_ep_api.ep_api_recreate', default = ''
			).strip() or False
		return api_recreate
	
	
	def _get_show_warnings(self):
		api_show_warnings = self.env['ir.config_parameter'].sudo().with_context(
			company_id = self.env.company.id
			).get_param(
			'bag_ep_api.ep_api_show_warnings', default = ''
			).strip() or False
		return api_show_warnings
	
	
	def _get_level_warnings(self):
		api_level_warnings = self.env['ir.config_parameter'].sudo().with_context(
			company_id = self.env.company.id
			).get_param(
			'bag_ep_api.ep_api_level_warnings', default = 'none'
			).strip() or False
		return api_level_warnings
	
	
	def _full_house_number_format(self, warnings):
		for record in self:
			record.house_number = False
			record.house_letter = False
			record.house_number_addition = False
			
			if not record.full_house_number:
				continue
			
			try:
				num, let, ext = self.parse_full_house_number(record.full_house_number)
				record.house_number = num
				record.house_letter = let
				record.house_number_addition = ext
			
			except UserError as e:
				
				warnings.append(
					f"ZIP -- Invalid House Number Format '{str(e)}' "
					)
		
		return None
	
	
	def _call_api_lookups(self, warnings):
		
		self._zip_auto_fill_address_sync(warnings)
		if not warnings:
			self._bag_auto_fill_address_sync(warnings)
		if not warnings:
			self._ep_auto_fill_address_sync(warnings)
		
		return warnings
	
	
	def action_reset_to_defaults(self):
		exclude_fields = {'id', 'create_uid', 'create_date', 'write_uid', 'write_date'}
		field_names = [f for f in self.fields_get().keys() if f not in exclude_fields]
		
		for record in self:
			defaults = record.default_get(field_names)
			record.write(defaults)
	
	
	def action_ep_api_lookup(self):
		"""Manual BAG fetch from the UI button."""
		for partner in self:
			parsed = BufferManager.get()
			if parsed:
				filtered_vals = filter_model_fields(self.env, 'ep.data', parsed.model_dump())
				ep_data_model = self.env['ep.data']
				existing = ep_data_model.search([('partner_id', '=', partner.id)], limit = 1)
				
				if existing:
					existing.write(filtered_vals)
	
	
	@staticmethod
	def parse_full_house_number(full_house_number):
		pattern = re.compile(r"^(\d+)([A-Za-z]?)(?:-(\d+))?$")
		match = pattern.match(full_house_number.strip())
		if not match:
			raise UserError(_("Invalid format. Use e.g. '70', '70A', '70-1', or '70A-1'."))
		
		return (
			int(match.group(1)),
			match.group(2) if match.group(2) else None,
			int(match.group(3)) if match.group(3) else None
			)
	
	
	def _zip_auto_fill_address_sync(self, warnings):
		"""Synchronous ZIP address autofill."""
		for partner in self:
			if not partner.zip or not partner.full_house_number:
				pass
			else:
				zip_client = self.env['zip.api.client']
				try:
					
					zip_response = zip_client.fetch_address(  # sync method required
						zipcode = partner.zip,
						full_house_number = partner.full_house_number,
						)
					if zip_response:
						state = self.env['res.country.state'].search(
							[
								('name', 'ilike', zip_response.provincie),
								], limit = 1
							)
						
						partner.street = f"{zip_response.straat} {zip_response.huisnummer}" or ''
						partner.city = zip_response.woonplaats or ''
						partner.country_id = self.env.ref('base.nl').id  # or use 165 if you must
						partner.state_id = state or False
						partner.ep_lookup_status = 1
						
						_logger.info(f"[Zip] Autofill completed for {partner.name}.")
						return None
					return None
				
				except Exception as e:
					_logger.warning(f"[Zip] Lookup failed for {partner.name}: {e}")
					
					partner.street = ''
					partner.city = ''
					partner.state_id = False
					
					warnings.append(
						f"ZIP -- Could not find address for zip '{partner.zip}' "
						f"and number '{partner.full_house_number}'."
						)
			
			return None
		return None
	
	
	def _bag_auto_fill_address_sync(self, warnings):
		"""Synchronous BAG address autofill."""
		for partner in self:
			if not partner.house_number:
				self._full_house_number_format(warnings)
			
			if partner.zip and partner.house_number:
				bag_client = self.env['bag.api.client']
				try:
					bag_response = bag_client.fetch_address(  # sync method required
						postcode = partner.zip.replace(' ', ''),
						huisnummer = partner.house_number,
						huisletter = partner.house_letter,
						huisnummertoevoeging = partner.house_number_addition,
						)
					if bag_response and bag_response.embedded and bag_response.embedded.adressen:
						
						if len(bag_response.embedded.adressen) > 1:
							_logger.warning(f"[BAG] Multiple addresses found for {partner.name}.")
							warnings.append(
								f"BAG -- Found a more BAG-IDs for zip: '{partner.zip}' "
								f"and number in the BAG register'{partner.full_house_number}'."
								)
							return
						
						adres = bag_response.embedded.adressen[0]
						# Adres of the bag into the buffer
						BufferManager.set(adres)
						
						partner.addressable_object = adres.adresseerbaarObjectIdentificatie
						partner.ep_lookup_status = 2
						
						_logger.info(f"[BAG] Autofill completed for {partner.name}.")
				
				except Exception as e:
					_logger.warning(f"[BAG] Lookup failed for {partner.name}: {e}")
					
					partner.street = ''
					partner.city = ''
					partner.state_id = False
					
					warnings.append(
						f"BAG -- Could not find address for zip: '{partner.zip}' "
						f"and number in the BAG register'{partner.full_house_number}'."
						)
	
	
	def _ep_auto_fill_address_sync(self, warnings):
		for partner in self:
			if not partner.exists():
				_logger.warning(f"Partner {partner} does not exist in DB.")
				continue
			
			if partner.addressable_object:
				try:
					parsed = self.env['ep.api.client'].fetch_with_address_object(
						adresseerbaar_object_id = partner.addressable_object,
						)
					# parsed is a Pydantic structure
					BufferManager.set(parsed)
					partner.ep_lookup_status = 3
				
				except Exception as e:
					_logger.exception(f"EP autofill failed {partner.name}: {e}")
					
					warnings.append(
						f"Ep-Online -- Could not find a Energy label for zip: '{partner.zip}' "
						f"and number in the EP-Online register'{partner.full_house_number}'."
						f"using the Usable Area and Construction Year from BAG register"
						)
