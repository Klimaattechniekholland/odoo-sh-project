import requests
import logging
from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class EpOnlineApiClient(models.AbstractModel):
    _name = "ep.online.api.client"
    _description = "EP-Online API Client"

    def _get_headers(self):
        token = self.env['ir.config_parameter'].sudo().get_param(
            'energy_label_integration.ep_online_api_key'
        )
        if not token:
            raise UserError("EP-Online API key is not configured.")
        return {"Authorization": token}

    def fetch_by_address(self, postcode, huisnummer, huisletter=None, toevoeging=None, verblijfsobject_id=None):
        base_url = 'https://public.ep-online.nl/api/v5/PandEnergielabel/Adres'
    
        params = {}
        if verblijfsobject_id:
            params['verblijfsobjectId'] = verblijfsobject_id
        else:
            params = {
                "postcode": postcode.replace(" ", "").upper(),
                "huisnummer": huisnummer
            }
            if huisletter:
                params["huisletter"] = huisletter
            if toevoeging:
                params["huisnummertoevoeging"] = toevoeging
    
        try:
            _logger.info(f"[EP-Online] Requesting: {base_url} with {params}")
            response = requests.get(base_url, headers=self._get_headers(), params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
    
            if not data:
                raise UserError("No data returned from EP-Online.")
    
            # handle list or dict
            main_data = data[0] if isinstance(data, list) else data
    
            return {
                'thermische_oppervlakte': main_data.get('Gebruiksoppervlakte_thermische_zone'),
                'energielabel': main_data.get('energielabel') or main_data.get('Energieklasse'),
                'energieindex': main_data.get('energieindex') or main_data.get('BerekendeEnergieverbruik'),
                'labelType': main_data.get('labelType') or main_data.get('Berekeningstype'),
                'geldigheidsdatum': main_data.get('geldigheidsdatum') or main_data.get('Geldig_tot'),
                'raw_response': data  # entire JSON for detailed use
            }
    
        except requests.RequestException as e:
            _logger.exception("[EP-Online] API call failed")
            raise UserError(f"Error connecting to EP-Online API: {e}")

