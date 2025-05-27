# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from ..utils.address_utils import parse_house_number
from datetime import datetime
import logging
import httpx

_logger = logging.getLogger(__name__)

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    # EP-Online API fields
    ep_energy_label = fields.Char(string="Energy Label", tracking=True)
    ep_energy_index = fields.Float(string="Energy Index (EP)", tracking=True)
    ep_label_type = fields.Char(string="Label Type", tracking=True)
    ep_validity_end = fields.Date(string="Label Valid Until", tracking=True)

    # BAG API fields
    bag_street = fields.Char(string="Street (BAG)", tracking=True)
    bag_city = fields.Char(string="City (BAG)", tracking=True)
    bag_verblijfsobject_id = fields.Char(string="BAG Verblijfsobject ID", tracking=True)
    bag_usage = fields.Char(string="Usage (BAG)", tracking=True)
    bag_construction_year = fields.Integer(string="Construction Year (BAG)", tracking=True)

    # Related fields to display partner address directly on CRM lead
    partner_street = fields.Char(related='partner_id.street', string="Street", store=True)
    partner_zip = fields.Char(related='partner_id.zip', string="Postcode", store=True)
    partner_city = fields.Char(related='partner_id.city', string="City", store=True)
    partner_huisnummer = fields.Char(related='partner_id.huisnummer', string="House Number", store=True)
    partner_huisletter = fields.Char(related='partner_id.huisletter', string="House Letter", store=True)
    partner_toevoeging = fields.Char(related='partner_id.huisnummertoevoeging', string="Number Addition", store=True)

    def write(self, vals):
        res = super().write(vals)
        if 'stage_id' in vals:
            for lead in self:
                if lead.stage_id.name == 'Voorlopige Offerte':
                    lead._fetch_energy_label(override=False)
        return res

    def action_fetch_ep_online(self):
        """Manual trigger to fetch EP-Online data only."""
        for lead in self:
            lead._fetch_ep_online(override=True)

    def action_refresh_energy_label(self):
        """Manual button to refresh energy label data."""
        for lead in self:
            lead._fetch_energy_label(override=True)



    def action_fetch_bag_api(self):
        """Call BAG API via service model and update lead + partner address fields."""
        for lead in self:
            partner = lead.partner_id
            if not partner or not partner.zip or not partner.huisnummer:
                raise UserError("Partner must have postcode and house number.")
    
            postcode = partner.zip.strip()
            huisnummer = partner.huisnummer.strip()
            huisletter = getattr(partner, 'huisletter', None)
            toevoeging = getattr(partner, 'huisnummertoevoeging', None)
    
            bag_client = self.env['bag.api.client']
    
            try:
                _logger.info(f"[BAG] Calling with postcode={postcode}, huisnummer={huisnummer}, huisletter={huisletter}, toevoeging={toevoeging}")
                result = bag_client.fetch_address(
                    postcode=postcode,
                    huisnummer=huisnummer,
                    huisletter=huisletter,
                    huisnummertoevoeging=toevoeging,
                )
    
                street = city = None
    
                # If AddressResponse (pydantic model) was returned
                if hasattr(result, 'embedded') and result.embedded.adressen:
                    adres = result.embedded.adressen[0]
                    street = adres.openbareRuimteNaam
                    city = adres.woonplaatsNaam
                    lead.bag_street = street
                    lead.bag_city = city
                    lead.bag_verblijfsobject_id = adres.adresseerbaarObjectIdentificatie
                    lead.bag_usage = ', '.join(adres.gebruiksdoelen or [])
                    if adres.oorspronkelijkBouwjaar and adres.oorspronkelijkBouwjaar[0].isdigit():
                        lead.bag_construction_year = int(adres.oorspronkelijkBouwjaar[0])
    
                # If raw dict (OGC fallback) was returned
                elif isinstance(result, dict) and 'features' in result and result['features']:
                    props = result['features'][0].get('properties', {})
                    street = props.get('openbareRuimteNaam')
                    city = props.get('woonplaatsNaam')
                    lead.bag_street = street
                    lead.bag_city = city
                    lead.bag_verblijfsobject_id = props.get('identificatie')
                    lead.bag_usage = props.get('gebruiksdoelVerblijfsobject', '')
                    bouwjaar = props.get('bouwjaar')
                    if bouwjaar and bouwjaar.isdigit():
                        lead.bag_construction_year = int(bouwjaar)
                else:
                    raise UserError("BAG API returned no valid data.")
    
                #  Update partner address too
                if street:
                    partner.street = street
                if city:
                    partner.city = city
    
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': "BAG API Success",
                        'message': f"Lead & partner updated. Street: {street}, City: {city}",
                        'sticky': False,
                    }
                }
    
            except Exception as e:
                _logger.exception("[BAG] Error occurred")
                raise UserError(f"BAG API error: {str(e)}")


    

    def _fetch_ep_online(self, override=False):
        """Fetch energy label from EP-Online API using service client and update lead fields."""
        partner = self.partner_id
        if not partner or not partner.zip or not partner.huisnummer:
            raise UserError("Partner must have postcode and house number.")

        postcode = partner.zip.strip().replace(" ", "").upper()
        number, letter, toevoeging = parse_house_number(partner.huisnummer.strip())

        try:
            huisnummer = int(number)
        except (TypeError, ValueError):
            raise UserError("Invalid house number format.")

        # Get EP-Online API client service
        ep_client = self.env['ep.online.api.client']
        try:
            label_data = ep_client.fetch_by_address(postcode, huisnummer, letter, toevoeging)
        except httpx.HTTPStatusError as e:
            _logger.error(f"[EP-Online] HTTP {e.response.status_code}: {e.response.text}")
            raise UserError(f"EP-Online request failed with status {e.response.status_code}")
        except Exception as e:
            _logger.exception("[EP-Online] Unexpected error")
            raise UserError(f"EP-Online failed: {str(e)}")

        if not isinstance(label_data, list) or not label_data:
            raise UserError("No energy label found via EP-Online.")

        label = label_data[0]
        _logger.info(f"[EP-Online] Label received: {label}")

        energy_label = label.get('Energieklasse')
        energy_index = label.get('BerekendeEnergieverbruik')
        label_type = label.get('Berekeningstype')
        validity_raw = label.get('Geldig_tot')

        validity_date = None
        if validity_raw:
            try:
                validity_date = datetime.fromisoformat(validity_raw).date()
            except Exception:
                _logger.warning(f"[EP-Online] Invalid date format for Geldig_tot: {validity_raw}")

        # Assign values only if not already set or if override is True
        if override or not self.ep_energy_label:
            self.ep_energy_label = energy_label
        if override or not self.ep_energy_index:
            self.ep_energy_index = float(energy_index) if energy_index else None
        if override or not self.ep_label_type:
            self.ep_label_type = label_type
        if override or not self.ep_validity_end:
            self.ep_validity_end = validity_date


    def _fetch_energy_label(self, override=False):
        """Fetch both BAG and EP-Online data via services for maximum field enrichment."""
        from ..utils.address_utils import parse_house_number
    
        partner = self.partner_id
        if not partner or not partner.zip or not partner.huisnummer:
            raise UserError("Partner must have postcode and house number.")
    
        postcode = partner.zip.strip().replace(" ", "").upper()
        raw_huisnummer = partner.huisnummer.strip()
        number, letter, toevoeging = parse_house_number(raw_huisnummer)
    
        try:
            huisnummer = int(number)
        except (TypeError, ValueError):
            raise UserError("Invalid house number format.")
    
        # === STEP 1: BAG API ===
        try:
            bag_client = self.env['bag.api.client']
            result = bag_client.fetch_address(
                postcode=postcode,
                huisnummer=huisnummer,
                huisletter=letter,
                huisnummertoevoeging=toevoeging,
            )
    
            street = city = None
    
            if hasattr(result, 'embedded') and result.embedded.adressen:
                adres = result.embedded.adressen[0]
                street = adres.openbareRuimteNaam
                city = adres.woonplaatsNaam
                self.bag_street = street
                self.bag_city = city
                self.bag_verblijfsobject_id = adres.adresseerbaarObjectIdentificatie
                self.bag_usage = ', '.join(adres.gebruiksdoelen or [])
                if adres.oorspronkelijkBouwjaar and adres.oorspronkelijkBouwjaar[0].isdigit():
                    self.bag_construction_year = int(adres.oorspronkelijkBouwjaar[0])
    
            elif isinstance(result, dict) and 'features' in result and result['features']:
                props = result['features'][0].get('properties', {})
                street = props.get('openbareRuimteNaam')
                city = props.get('woonplaatsNaam')
                self.bag_street = street
                self.bag_city = city
                self.bag_verblijfsobject_id = props.get('identificatie')
                self.bag_usage = props.get('gebruiksdoelVerblijfsobject', '')
                bouwjaar = props.get('bouwjaar')
                if bouwjaar and bouwjaar.isdigit():
                    self.bag_construction_year = int(bouwjaar)
            else:
                _logger.warning("[BAG] No usable data returned.")
    
            # Update partner too
            if street:
                partner.street = street
            if city:
                partner.city = city
    
        except Exception as e:
            _logger.warning(f"[BAG] Silent failure: {e}")
    
        # === STEP 2: EP-Online API ===
        try:
            ep_client = self.env['ep.online.api.client']
            label_data = ep_client.fetch_by_address(
                postcode=postcode,
                huisnummer=huisnummer,
                huisletter=letter,
                toevoeging=toevoeging,
            )
        except httpx.HTTPStatusError as e:
            _logger.error(f"[EP-Online] HTTP {e.response.status_code}: {e.response.text}")
            raise UserError(f"EP-Online request failed with status {e.response.status_code}")
        except Exception as e:
            _logger.exception("[EP-Online] Unexpected error")
            raise UserError(f"EP-Online failed: {str(e)}")
    
        if not isinstance(label_data, list) or not label_data:
            raise UserError("No energy label found via EP-Online.")
    
        label = label_data[0]
        _logger.info(f"[EP-Online] Label received: {label}")
    
        energy_label = label.get('Energieklasse')
        energy_index = label.get('BerekendeEnergieverbruik')
        label_type = label.get('Berekeningstype')
        validity_raw = label.get('Geldig_tot')
    
        validity_date = None
        if validity_raw:
            try:
                validity_date = datetime.fromisoformat(validity_raw).date()
            except Exception:
                _logger.warning(f"[EP-Online] Invalid date format for Geldig_tot: {validity_raw}")
    
        if override or not self.ep_energy_label:
            self.ep_energy_label = energy_label
        if override or not self.ep_energy_index:
            self.ep_energy_index = float(energy_index) if energy_index else None
        if override or not self.ep_label_type:
            self.ep_label_type = label_type
        if override or not self.ep_validity_end:
            self.ep_validity_end = validity_date


