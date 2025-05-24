import logging
from odoo import models

_logger = logging.getLogger(__name__)


class BagApiClientError(Exception):
    """Custom error for BAG API client."""


class BagApiClient(models.AbstractModel):
    _name = "bag.api.client"
    _description = "BAG API Client"

    V2_BASE_URL = "https://api.bag.kadaster.nl/lvbag/individuelebevragingen/v2"
    OGC_BASE_URL = "https://api.pdok.nl/lv/bag/ogc/v1"

    def _get_headers(self):
        """Fetch API key and set headers."""
        api_key = self.env['ir.config_parameter'].sudo().get_param('bag_api.api_key')
        return {
            "Accept-Crs": "epsg:28992",
            "X-Api-Key": api_key or "l787f9dabe8e144ae5895e74ca8ee39f6b",
        }

    def fetch_address(self, postcode, huisnummer, huisletter=None, huisnummertoevoeging=None, exact_match=False):
        # Lazy import to avoid Odoo import issues
        import httpx
        from ..services.bag_models import AddressResponse

        try:
            # 1. Authenticated V2 call
            v2_url = f"{self.V2_BASE_URL}/adressenuitgebreid"
            headers = self._get_headers()
            params = {
                "postcode": postcode.replace(" ", "").upper(),
                "huisnummer": huisnummer,
            }
            if huisletter:
                params["huisletter"] = huisletter
            if huisnummertoevoeging:
                params["huisnummertoevoeging"] = huisnummertoevoeging
            if exact_match:
                params["exacteMatch"] = "true"

            _logger.info(f"[BAG API] Trying authenticated BAG V2 with params: {params}")

            with httpx.Client(timeout=10.0) as client:
                response = client.get(v2_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                parsed = AddressResponse.model_validate(data)
                _logger.debug(f"[BAG API] Parsed V2 response: {parsed}")
                return parsed

        except Exception as e:
            _logger.warning(f"[BAG API] V2 failed, falling back to OGC. Reason: {e}")

        # 2. Fallback: Public OGC
        try:
            ogc_url = f"{self.OGC_BASE_URL}/nummeraanduiding"
            ogc_params = {
                "postcode": postcode.replace(" ", "").upper(),
                "huisnummer": huisnummer,
                "f": "json"
            }
            _logger.info(f"[BAG API] Trying OGC fallback with params: {ogc_params}")

            with httpx.Client(timeout=10.0) as client:
                res = client.get(ogc_url, params=ogc_params)
                res.raise_for_status()
                ogc_data = res.json()
                _logger.debug(f"[BAG API] Fallback OGC response: {ogc_data}")
                return ogc_data

        except Exception as e:
            _logger.exception("[BAG API] Fallback OGC also failed.")
            raise BagApiClientError(f"Both V2 and OGC failed: {str(e)}") from e
