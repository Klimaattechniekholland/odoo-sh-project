# models/__init__.py
from . import energy_label_models

# models/energy_label_models.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging, requests

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    energy_house_number = fields.Integer(string="House Number")
    energy_house_letter = fields.Char(string="House Letter", size=5)
    energy_house_addition = fields.Char(string="House Addition", size=10)
    energy_label_class = fields.Char(string="Energy Label Class")
    energy_index = fields.Float(string="Energy Index", digits=(3, 2))
    energy_year_built = fields.Integer(string="Year Built")
    energy_usable_area = fields.Float(string="Usable Surface Area (m²)")

    def action_fetch_energy_data(self):
        for lead in self:
            if not lead.zip or not lead.energy_house_number:
                raise UserError(_("Please enter Postcode (ZIP) and House Number before fetching energy data."))

            ep_api_key = self.env['ir.config_parameter'].sudo().get_param('energy_label.ep_online_api_key')
            bag_api_key = self.env['ir.config_parameter'].sudo().get_param('energy_label.bag_pdok_api_key')
            if not ep_api_key:
                raise UserError(_("EP-Online API key is not configured. Please set it in System Parameters."))

            postcode_nospace = lead.zip.replace(' ', '')
            ep_url = f"https://public.ep-online.nl/api/v5/PandEnergielabel/Adres?postcode={postcode_nospace}&huisnummer={int(lead.energy_house_number)}"
            if lead.energy_house_letter:
                ep_url += f"&huisletter={lead.energy_house_letter}"
            if lead.energy_house_addition:
                ep_url += f"&huisnummertoevoeging={lead.energy_house_addition}"

            headers = {"X-Api-Key": ep_api_key}
            energy_class = energy_index = year_built = surface = None
            try:
                _logger.info("Calling EP-Online API for %s, URL: %s", lead.name, ep_url)
                response = requests.get(ep_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    energy_class = data.get('energielabel') or data.get('label')
                    energy_index = data.get('energieIndex') or data.get('energy_index')
                    year_built = data.get('bouwjaar') or data.get('yearBuilt')
                    surface = data.get('oppervlakte') or data.get('usableArea')
            except Exception as e:
                _logger.error("EP-Online API call failed for %s: %s", lead.name, str(e))

            if not year_built or not surface:
                bag_url = f"https://api.pdok.nl/lv/bag/lookup/v1/lookup?postcode={postcode_nospace}&huisnummer={int(lead.energy_house_number)}"
                if lead.energy_house_letter:
                    bag_url += f"{lead.energy_house_letter}"
                if lead.energy_house_addition:
                    bag_url += f"&toev={lead.energy_house_addition}"
                try:
                    _logger.info("Calling BAG PDOK API for %s, URL: %s", lead.name, bag_url)
                    bag_resp = requests.get(bag_url, headers={"X-Api-Key": bag_api_key} if bag_api_key else {}, timeout=10)
                    if bag_resp.status_code == 200:
                        bag_data = bag_resp.json()
                        year_built = year_built or bag_data.get('bouwjaar') or bag_data.get('yearBuilt')
                        surface = surface or bag_data.get('oppervlakte') or bag_data.get('area')
                except Exception as e:
                    _logger.error("BAG PDOK API call failed for %s: %s", lead.name, str(e))

            lead.write({
                'energy_label_class': energy_class or 'C',
                'energy_index': energy_index or 1.50,
                'energy_year_built': year_built or 0,
                'energy_usable_area': surface or 0.0
            })