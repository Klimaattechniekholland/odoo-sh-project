# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError
from . import services

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # EP-Online fields (same names/meaning as in crm.lead)
    ep_energy_label = fields.Char(string="Energy Label", tracking=True)
    ep_energy_index = fields.Float(string="Energy Index (EP)", tracking=True)
    ep_label_type = fields.Char(string="Label Type", tracking=True)
    ep_validity_end = fields.Date(string="Label Valid Until", tracking=True)
    # BAG fields
    bag_street = fields.Char(string="Street (BAG)", tracking=True)
    bag_city = fields.Char(string="City (BAG)", tracking=True)
    bag_verblijfsobject_id = fields.Char(string="BAG Verblijfsobject ID", tracking=True)
    bag_usage = fields.Char(string="Usage (BAG)", tracking=True)
    bag_construction_year = fields.Integer(string="Construction Year (BAG)", tracking=True)

    def action_refresh_energy_label(self):
        """ Button action: refresh data for sale order. """
        for order in self:
            # Use partner_id address
            partner = order.partner_shipping_id or order.partner_id
            if not partner.zip or not partner.street:
                raise UserError("Shipping address incomplete for energy lookup.")
            postcode = partner.zip
            huisnummer = partner.huisnummer or 0
            huisletter = partner.huisletter or ''
            toevoeging = partner.huisnummertoevoeging or ''
            # Init clients
            ep_key = self.env['ir.config_parameter'].sudo().get_param('energy_label_integration.ep_online_api_key')
            bag_key = self.env['ir.config_parameter'].sudo().get_param('energy_label_integration.bag_api_key')
            ep_client = services.EpOnlineClient(api_key=ep_key)
            bag_client = services.BagApiClient(api_key=bag_key)
            # EP-Online by address
            ep_data = ep_client.get_by_address(postcode, huisnummer, huisletter, toevoeging)
            if not ep_data or not ep_data.get('energy_label'):
                bag_data = bag_client.get_nummeraanduiding(postcode, huisnummer, huisletter, toevoeging)
                bag_id = None
                if bag_data and '_embedded' in bag_data:
                    addr = bag_data['_embedded']['nummeraanduiding'][0]
                    self.bag_street = addr.get('openbareruimte', {}).get('naam')
                    self.bag_city = addr.get('woonplaatsNaam')
                    verblijfs = addr.get('verblijfsobjecten')
                    if verblijfs:
                        bag_id = verblijfs[0].get('identificatie')
                if bag_id:
                    ep_data = ep_client.get_by_bag(bag_id)
            if not ep_data or not ep_data.get('energy_label'):
                # Fallback record
                self.env['energy.label.fallback'].create({
                    'postcode': postcode,
                    'huisnummer': huisnummer,
                    'huisletter': huisletter,
                    'huisnummertoevoeging': toevoeging,
                })
                raise UserError("Energy label data not found (fallback record created).")
            # Update fields
            if ep_data:
                self.ep_energy_label = ep_data.get('energy_label')
                self.ep_energy_index = ep_data.get('energy_index')
                self.ep_validity_end = ep_data.get('validity_end')
