import logging
import httpx
from odoo import models
from odoo.addons.bag_ep_api.services.base_models.zip_basemodel import \
	ZipData  # Ensure this returns a data class or parsed dict


_logger = logging.getLogger(__name__)


class ZipApiClientError(Exception):
	"""Custom error for ZIP_API_client."""


class ZipApiClient(models.AbstractModel):
	_name = "zip.api.client"
	_description = "ZIP API Client"
	
	
	@staticmethod
	def _get_url():
		return "https://openpostcode.nl/api/address"
	
	
	# api_url = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id).get_param(
	# 	'bag_ep_api.zip_api_url', default = ''
	# 	).strip() or "https://openpostcode.nl/api/address"
	# return api_url
	
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
			raise ZipApiClientError(f"Network error while contacting BAG API: {str(e)}") from e
		
		except httpx.HTTPStatusError as e:
			_logger.error(f"[ZIP API] HTTP error: {e.response.status_code} - {e.response.text}")
			raise ZipApiClientError(f"HTTP error: {e.response.status_code}") from e
		
		except Exception as e:
			_logger.exception("[ZIP API] Unexpected error during call")
			raise ZipApiClientError(f"Unexpected error: {str(e)}") from e
