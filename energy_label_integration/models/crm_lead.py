from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ..services.bag_api_client import BagApiClient
from ..services.ep_online_client import EpOnlineApiClient
from ..utils.address_utils import parse_house_number
import json
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Related partner address fields (editable)
    partner_street = fields.Char(related='partner_id.street', string="Street", store=True, readonly=False)
    partner_zip = fields.Char(related='partner_id.zip', string="Postcode", store=True, readonly=False)
    partner_city = fields.Char(related='partner_id.city', string="City", store=True, readonly=False)
    partner_huisnummer = fields.Char(related='partner_id.huisnummer', string="House Number", store=True, readonly=False)
    partner_huisletter = fields.Char(related='partner_id.huisletter', string="House Letter", store=True, readonly=False)
    partner_toevoeging = fields.Char(related='partner_id.huisnummertoevoeging', string="Number Addition", store=True, readonly=False)

    # Manual override flag
    energy_data_manual_override = fields.Boolean(string='Manual Override')

    # EP-Online fields
    ep_energy_label = fields.Char(string='Energy Label')
    ep_energy_index = fields.Float(string='Energy Index')
    ep_label_type = fields.Char(string='Label Type')
    ep_validity_end = fields.Date(string='Label Validity End')
    ep_thermische_oppervlakte = fields.Float(string='Thermal Area (m²)')

    # BAG fields
    bag_street = fields.Char(string='BAG Street')
    bag_city = fields.Char(string='BAG City')
    bag_verblijfsobject_id = fields.Char(string='BAG Address Object ID')
    bag_usage = fields.Char(string='BAG Usage')
    bag_construction_year = fields.Integer(string='BAG Construction Year')
    bag_oppervlakte = fields.Float(string='BAG Area (m²)')

    # Other fields
    carbon_emissions = fields.Float(string='CO₂ Emissions (kg/year)')
    api_raw_response = fields.Text(string='API Raw Response')

    def to_serializable(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return str(obj)

    def _get_address_components(self):
        postcode = (self.partner_zip or '').replace(" ", "").upper()
        huisnummer = self.partner_huisnummer or ''
        toevoeging = self.partner_toevoeging or ''
        letter = self.partner_huisletter or ''
        return postcode, huisnummer, toevoeging, letter

    def _clear_energy_fields(self):
        self.ep_energy_label = False
        self.ep_energy_index = False
        self.ep_label_type = False
        self.ep_validity_end = False
        self.ep_thermische_oppervlakte = False
        self.bag_street = False
        self.bag_city = False
        self.bag_verblijfsobject_id = False
        self.bag_usage = False
        self.bag_construction_year = False
        self.bag_oppervlakte = False
        self.carbon_emissions = False
        self.api_raw_response = False

    def _fetch_all_data(self):
        ep_client = self.env['ep.online.api.client']
        bag_client = self.env['bag.api.client']

        for lead in self:
            if lead.energy_data_manual_override:
                continue

            postcode, huisnummer, toevoeging, letter = lead._get_address_components()
            lead._clear_energy_fields()

            if not huisnummer.isdigit():
                raise UserError(f"Invalid house number: '{huisnummer}'")

            ep_data = {}
            bag_data = {}

            try:
                ep_data = ep_client.fetch_by_address(postcode, huisnummer, letter, toevoeging)
                _logger.info("[EP] Data fetched by address: %s", ep_data)
            except Exception as e:
                _logger.warning("[EP] Fetch failed: %s", e)

            try:
                bag_data = bag_client.fetch_address(postcode, huisnummer, letter, toevoeging)
                _logger.info("[BAG] Data fetched: %s", bag_data)
            except Exception as e:
                _logger.warning("[BAG] Fetch failed: %s", e)

            if not ep_data and hasattr(bag_data, 'embedded') and bag_data.embedded.adressen:
                vbo_id = bag_data.embedded.adressen[0].adresseerbaarObjectIdentificatie
                try:
                    ep_data = ep_client.fetch_by_address(postcode, huisnummer, letter, toevoeging, vbo_id)
                    _logger.info("[EP] Retried with BAG ID: %s", ep_data)
                except Exception as e:
                    _logger.warning("[EP] Retry with BAG ID failed: %s", e)

            lead._populate_ep_data(ep_data)
            lead._populate_bag_data(bag_data)

            try:
                combined_data = {
                    "ep_online": ep_data,
                    "bag": to_serializable(bag_data)
                }
                lead.api_raw_response = f"<pre>{json.dumps(combined_data, indent=2, ensure_ascii=False)}</pre>"
            except Exception as e:
                _logger.warning(f"Failed to serialize combined API data: {e}")
                lead.api_raw_response = str({
                    "ep_online": str(ep_data),
                    "bag": str(bag_data)
                })

    def _populate_ep_data(self, ep_data):
        if not ep_data:
            return
        self.ep_energy_label = ep_data.get('energielabel')
        self.ep_energy_index = ep_data.get('energieindex')
        self.ep_label_type = ep_data.get('labelType')
        self.ep_validity_end = ep_data.get('geldigheidsdatum')
        self.ep_thermische_oppervlakte = ep_data.get('thermische_oppervlakte')

    def _populate_bag_data(self, bag_data):
        if not bag_data or not hasattr(bag_data, 'embedded') or not bag_data.embedded.adressen:
            return

        adres = bag_data.embedded.adressen[0]
        self.bag_street = adres.openbareRuimteNaam
        self.bag_city = adres.woonplaatsNaam
        self.bag_verblijfsobject_id = adres.adresseerbaarObjectIdentificatie
        self.bag_usage = ', '.join(adres.gebruiksdoelen or [])
        self.bag_construction_year = int(adres.oorspronkelijkBouwjaar[0]) if adres.oorspronkelijkBouwjaar else None
        self.bag_oppervlakte = adres.oppervlakte

        if self.partner_id:
            if adres.openbareRuimteNaam:
                self.partner_id.street = adres.openbareRuimteNaam
            if adres.woonplaatsNaam:
                self.partner_id.city = adres.woonplaatsNaam

    def write(self, vals):
        if 'energy_data_manual_override' in vals and vals['energy_data_manual_override']:
            return super().write(vals)

        trigger = False
        if 'stage_id' in vals:
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            if new_stage and new_stage.name == 'Voorlopige Offerte':
                trigger = True
        res = super().write(vals)
        if trigger:
            self._fetch_all_data()
        return res

    def action_fetch_data(self):
        self._fetch_all_data()
        return self._notify_user(_('Data Fetch'), _('EP-Online and BAG data fetched successfully.'))

    def action_test_ep(self):
        try:
            postcode, huisnummer, toevoeging, letter = self._get_address_components()
            ep_data = self.env['ep.online.api.client'].fetch_by_address(postcode, huisnummer, letter, toevoeging)
            self._populate_ep_data(ep_data)
            return self._notify_user(_('EP-Online Test'), _('EP-Online data fetched successfully.'))
        except Exception as e:
            raise UserError(_('EP-Online API test failed: %s') % e)

    def action_test_bag(self):
        try:
            postcode, huisnummer, toevoeging, letter = self._get_address_components()
            bag_data = self.env['bag.api.client'].fetch_address(postcode, huisnummer, letter, toevoeging)
            self._populate_bag_data(bag_data)
            return self._notify_user(_('BAG Test'), _('BAG data fetched successfully.'))
        except Exception as e:
            raise UserError(_('BAG API test failed: %s') % e)

    def _notify_user(self, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': 'success',
                'sticky': False
            }
        }
