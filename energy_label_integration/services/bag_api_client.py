import logging
import httpx
from odoo import models
from odoo.exceptions import UserError
from ..services.bag_models import AddressResponse
from ..utils.address_utils import parse_house_number

_logger = logging.getLogger(__name__)


class BagApiClientError(Exception):
    """Custom error for BAG API client."""


class BagApiClient(models.AbstractModel):
    _name = "bag.api.client"
    _description = "BAG API Client"

    V2_BASE_URL = "https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2/adressenuitgebreid"
    OGC_BASE_URL = "https://api.pdok.nl/lv/bag/ogc/v1/nummeraanduiding"

    def _get_headers(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('energy_label_integration.bag_api_key')
        if not api_key:
            return None
        return {
            "Accept-Crs": "epsg:28992",
            "X-Api-Key": api_key,
        }

    def fetch_address(self, postcode, huisnummer_raw, huisletter=None, huisnummertoevoeging=None, exact_match=False):
        postcode = postcode.replace(" ", "").upper()

        # Normalize house number using utility
        huisnummer, parsed_toevoeging, parsed_letter = parse_house_number(str(huisnummer_raw))

        # Prioritize explicitly passed parameters
        toevoeging = huisnummertoevoeging or parsed_toevoeging
        letter = huisletter or parsed_letter

        if not str(huisnummer).isdigit():
            raise UserError(f"Invalid house number provided to BAG API: '{huisnummer_raw}'")

        params = {
            "postcode": postcode,
            "huisnummer": huisnummer,
        }
        if letter:
            params["huisletter"] = letter
        if toevoeging:
            params["huisnummertoevoeging"] = toevoeging
        if exact_match:
            params["exacteMatch"] = "true"

        headers = self._get_headers()

        if headers:
            try:
                _logger.info(f"[BAG API] V2 request with params: {params}")
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(self.V2_BASE_URL, headers=headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    return AddressResponse.model_validate(data)
            except Exception as e:
                _logger.warning(f"[BAG API] V2 request failed: {e}. Trying OGC fallback.")

        # Fallback to public OGC API (open access)
        try:
            ogc_params = {
                "postcode": postcode,
                "huisnummer": huisnummer,
                "f": "json"
            }
            _logger.info(f"[BAG API] OGC fallback with params: {ogc_params}")
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.OGC_BASE_URL, params=ogc_params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            _logger.exception("[BAG API] Fallback OGC also failed.")
            raise BagApiClientError(f"Both V2 and OGC failed: {str(e)}") from e
