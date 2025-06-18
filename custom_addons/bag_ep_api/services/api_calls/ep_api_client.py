import logging
import httpx
from odoo import models
from odoo.addons.bag_ep_api.services.base_models.ep_basemodel import EpDataSchema


# from odoo.addons.bag_ep_api.services.base_models.ep_basemodel import \
# 	EpData  # Ensure this returns a data class or parsed dict

_logger = logging.getLogger(__name__)


class EpApiClientError(Exception):
	"""Custom error for Ep_API_client."""


class EpApiClient(models.AbstractModel):
	_name = "ep.api.client"
	_description = "Ep-Online API Client"
	
	
	@staticmethod
	def _get_url():
		return "https://public.ep-online.nl/api/v5/PandEnergielabel"
	
	
	# api_url = self.env['ir.config_parameter'].sudo().with_context(company_id = self.env.company.id).get_param(
	# 	'bag_ep_api.ep_api_url', default = ''
	# 	).strip() or  "https://public.ep-online.nl/api/v5/PandEnergielabel"
	# return api_url
	
	def _get_headers(self):
		"""Fetch API_key and set required headers."""
		api_key = self.env['ir.config_parameter'].sudo().get_param(
			'bag_ep_api.ep_api_key'
			) or "NEU5RTIyNUIyNkFDNkM5RDY2M0NFODAwMzlEMDAyMzU2MzIyQzEzNzhGNDEzRDA3OEJCNTdBQjQxOTQ2RDc1MkIyNTFCRjc3ODg2RTlFN0NFM0FFNUI5Mzc5M0YyQjk3"
		return {
			"Authorization": api_key,
			}
	
	
	def fetch_with_address_object(self, adresseerbaar_object_id):
		url = f"{self._get_url()}/AdresseerbaarObject/{adresseerbaar_object_id}"
		
		headers = self._get_headers()
		try:
			with httpx.Client(timeout = 10.0) as client:
				_logger.info(f"[EP API] Fetching adresseerbaar object with id: {adresseerbaar_object_id}")
				response = client.get(url, headers = headers)
				response.raise_for_status()
				
				data = response.json()
				_logger.debug(f"[EP API] Response data: {data}")
				
				parsed_list = [EpDataSchema.model_validate(item) for item in data]
				
				if len(parsed_list) == 1:
					parsed = parsed_list[0]
					_logger.debug(f"[EP API] Parsed EpDataSchema: {parsed.model_dump()}")
					return parsed
				
				elif not parsed_list:
					_logger.warning("[EP API] No records returned.")
				else:
					_logger.warning(f"[EP API] Multiple records returned ({len(parsed_list)}); expected 1.")
				
				return None
		
		except Exception as e:
			_logger.exception("[EP API] Unexpected error during call object")
			raise EpApiClientError(f"Unexpected error: {str(e)}") from e
		
		except httpx.RequestError as e:
			_logger.error(f"[EP API] Network error: {e}")
			raise EpApiClientError(f"Network error while contacting EP API: {str(e)}") from e
		
		except httpx.HTTPStatusError as e:
			_logger.error(f"[EP API] HTTP error: {e.response.status_code} - {e.response.text}")
			raise EpApiClientError(f"HTTP error: {e.response.status_code}") from e

# def fetch_with_address(self, postcode, huisnummer, huisletter = None, huisnummertoevoeging = None):
# 	url = f"{self._get_url()}/Adres"
#
# 	params = {
# 		"postcode": postcode,
# 		"huisnummer": huisnummer,
# 		}
# 	if huisletter:
# 		params["huisletter"] = huisletter
# 	if huisnummertoevoeging:
# 		params["huisnummertoevoeging"] = huisnummertoevoeging
#
# 	headers = self._get_headers()
#
# 	try:
# 		with httpx.Client(timeout = 10.0) as client:
#
# 			_logger.info(f"[BAG API] Fetching address with params: {params}")
#
# 			response = client.get(url, headers = headers, params = params)
# 			response.raise_for_status()
#
# 			data = response.json()
# 			_logger.debug(f"[BAG API] Response data: {data}")
#
# 			# Parse using list comprehension with `model_validate` (Pydantic v2)
# 			parsed_list = [EpDataSchema.model_validate(item) for item in data]
#
# 			if len(parsed_list) == 1:
# 				parsed = parsed_list[0]
# 				_logger.debug(f"[EP API] Parsed EpDataSchema: {parsed.model_dump()}")
# 				return parsed
# 			elif not parsed_list:
# 				_logger.warning("[EP API] No records returned.")
# 			else:
# 				_logger.warning(f"[EP API] Multiple records returned ({len(parsed_list)}); expected 1.")
#
# 			return None
#
# 	except httpx.RequestError as e:
# 		_logger.error(f"[EP API] Network error: {e}")
# 		raise EpApiClientError(f"Network error while contacting EP API: {str(e)}") from e
#
# 	except httpx.HTTPStatusError as e:
# 		_logger.error(f"[EP API] HTTP error: {e.response.status_code} - {e.response.text}")
# 		raise EpApiClientError(f"HTTP error: {e.response.status_code}") from e
#
# 	except Exception as e:
# 		_logger.exception("[EP API] Unexpected error during call")
# 		raise EpApiClientError(f"Unexpected error: {str(e)}") from e
