import logging
import httpx

from odoo.addons.bag_ep_api.services.api_calls.base_resolver import BaseEpResolver
from odoo.addons.bag_ep_api.services.base_models.zip_basemodel import ZipData
from odoo.addons.bag_ep_api.utils.buffer_manager import BufferManager


_logger = logging.getLogger(__name__)


class ZipApiClientError(Exception):
	"""Custom error for ZIP_API_client."""


class ZipApiResolver(BaseEpResolver):
	
	def _init_client(self):
		return ZipApiClient(self.env)
	
	
	def _call_api(self, partner):
		return self.client.fetch_address(
			zipcode = partner.zip,
			full_house_number = partner.full_house_number,
			)
	
	
	def _source_prefix(self):
		return "ZIP"
	
	
	def values_from_data(self, zip_data):
		if not zip_data:
			return None
		
		parsed_values = {}
		
		state = self.env['res.country.state'].search(
			[('name', 'ilike', zip_data.provincie)],
			limit = 1
			)
		
		parsed_values['street'] = f"{zip_data.straat} {zip_data.huisnummer}" or ''
		parsed_values['city'] = zip_data.woonplaats or ''
		parsed_values['state_id'] = state or False
		parsed_values['country_id'] = self.env.ref('base.nl').id
		parsed_values['ep_lookup_status'] = 1

		return parsed_values
	
	
	def fields_from_data(self, zip_data):
		if not zip_data:
			return None
		
		state = self.env['res.country.state'].search(
			[('name', 'ilike', zip_data.provincie)],
			limit = 1
			)
		
		self.partner.street = f"{zip_data.straat} {zip_data.huisnummer}" or ''
		self.partner.city = zip_data.woonplaats or ''
		self.partner.state_id = state or False
		self.partner.country_id = self.env.ref('base.nl').id
		self.partner.ep_lookup_status = 1
		BufferManager.set(self.env.user.id,'ep_lookup_status',1 )
		return None


class ZipApiClient:
	def __init__(self, env = None):
		self.env = env
	
	
	@staticmethod
	def _get_url():
		return "https://openpostcode.nl/api/address"
	
	
	def fetch_address(self, zipcode, full_house_number):
		url = f"{self._get_url()}"
		params = {
			"postcode": zipcode.replace(' ', '').upper(),
			"huisnummer": full_house_number,
			}
		try:
			with httpx.Client(timeout = 10.0) as client:
				_logger.info(f"[BAG API] Fetching address with params: {params}")
				response = client.get(url, params = params)
				response.raise_for_status()
				
				data = response.json()
				_logger.debug(f"[ZIP API] Response data: {data}")
				parsed = ZipData.model_validate(data)
				_logger.debug(f"[ZIP API] Parsed AddressResponse attributes: {vars(parsed)}")
				
				return parsed
		
		except httpx.RequestError as e:
			_logger.error(f"[ZIP API] Network error: {e}")
			raise ZipApiClientError(f"Network error while contacting ZIP API: {str(e)}") from e
		
		except httpx.HTTPStatusError as e:
			_logger.error(f"[ZIP API] HTTP error: {e.response.status_code} - {e.response.text}")
			raise ZipApiClientError(f"HTTP error: {e.response.status_code}") from e
		
		except Exception as e:
			_logger.exception("[ZIP API] Unexpected error during call")
			raise ZipApiClientError(f"Unexpected error: {str(e)}") from e
