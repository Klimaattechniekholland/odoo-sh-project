import logging
import httpx
from odoo.addons.bag_ep_api.services.api_calls.base_resolver import BaseEpResolver
from odoo.addons.bag_ep_api.services.base_models.bag_basemodel import \
	AddressResponse  # Ensure this returns a data class or parsed dict
from odoo.addons.bag_ep_api.utils.parse_full_house_number import parse_full_house_number


_logger = logging.getLogger(__name__)


class BagApiClientError(Exception):
	"""Custom error for BAG_API_client."""


class BagApiResolver(BaseEpResolver):
	def _init_client(self):
		return BagApiClient(self.env)
	
	
	def _call_api(self, partner):
		
		house_number, house_letter, house_number_addition = parse_full_house_number(partner.full_house_number)
		
		return self.client.fetch_address(
			postcode = partner.zip.replace(' ', ''),
			huisnummer = house_number,
			huisletter = house_letter,
			huisnummertoevoeging = house_number_addition,
			)
	

	def _source_prefix(self):
		return "BAG"
	
	
	def apply_from_data(self, bag_data, warnings = None, cache = True):
		if not bag_data or warnings:
			return None
		
		embedded = getattr(bag_data, "embedded", None)
		adressen = getattr(embedded, "adressen", None) if embedded else None
		
		if not embedded or not adressen:
			_logger.warning(f"[BAG] No address found for {self.partner.name}.")
			warnings.append(
				f"BAG — No addresses found for zip '{self.partner.zip}' "
				f"and number '{self.partner.full_house_number}'."
				)
			return None, warnings
		
		if len(adressen) > 1:
			_logger.warning(f"[BAG] Multiple addresses found for {self.partner.name}.")
			warnings.append(
				f"BAG — Multiple addresses found for zip '{self.partner.zip}' "
				f"and number '{self.partner.full_house_number}'."
				)
			return None, warnings
		
		adres = adressen[0]
		
		# Apply to partner
		self.partner.addressable_object = adres.adresseerbaarObjectIdentificatie
		self.partner.ep_lookup_status = 2
		
		# Optionally refresh cache
		if cache:
			self._get_cache()[self._cache_key()] = bag_data
		
		_logger.info(f"[BAG] Autofill completed for {self.partner.name}.")
		return adres, warnings


class BagApiClient:
	
	#  next option to set to more adressen, need to add a new view for selection
	MODEL = "adressenuitgebreid"

	def __init__(self, env = None):
		self.env = env
	
	def _get_headers(self):
		"""Fetch API_key and set required headers."""
		api_key = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id).get_param(
			'bag_ep_api.bag_api_key', default = ''
			).strip() or "l787f9dabe8e144ae5895e74ca8ee39f6b"
		
		return {
			"Accept-Crs": "epsg:28992",
			# 'accept:': 'application/hal+json',
			'X-Api-Key': api_key,
			}
	
	
	@staticmethod
	def _get_url():
		return "https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2/"
	
	
	# 	api_url = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id).get_param(
	# 		'bag_ep_api.bag_api_url', default = ''
	# 		).strip() or "https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2/"
	# 		# ensure that the last '/' is set
	# 	return api_url.rstrip('/') + '/'
	
	
	def _get_exact_match(self):
		api_exact_match = self.env['ir.config_parameter'].sudo().with_context(
			company_id = self.env.company.id
			).get_param(
			'bag_ep_api.bag_api_exact_match', default = ''
			).strip() or False
		return api_exact_match
	
	
	def fetch_address(self, postcode, huisnummer, huisletter = None, huisnummertoevoeging = None):
		
		url = f"{self._get_url()}{self.MODEL}"
		exact_match = self._get_exact_match()
		
		params = {
			"postcode": postcode,
			"huisnummer": huisnummer,
			}
		if huisletter:
			params["huisletter"] = huisletter
		if huisnummertoevoeging:
			params["huisnummertoevoeging"] = huisnummertoevoeging
		if exact_match:
			params["exacteMatch"] = "true"
		
		headers = self._get_headers()
		
		try:
			with httpx.Client(timeout = 10.0) as client:
				_logger.info(f"[BAG API] Fetching address with params: {params}")
				response = client.get(url, headers = headers, params = params)
				response.raise_for_status()
				
				data = response.json()
				_logger.debug(f"[BAG API] Response data: {data}")
				parsed = AddressResponse.model_validate(data)
				
				_logger.debug(f"[BAG API] Parsed AddressResponse attributes: {vars(parsed)}")
				return parsed
		
		except httpx.RequestError as e:
			_logger.error(f"[BAG API] Network error: {e}")
			raise BagApiClientError(f"Network error while contacting BAG API: {str(e)}") from e
		
		except httpx.HTTPStatusError as e:
			_logger.error(f"[BAG API] HTTP error: {e.response.status_code} - {e.response.text}")
			raise BagApiClientError(f"HTTP error: {e.response.status_code}") from e
		
		except Exception as e:
			_logger.exception("[BAG API] Unexpected error during call")
			raise BagApiClientError(f"Unexpected error: {str(e)}") from e
