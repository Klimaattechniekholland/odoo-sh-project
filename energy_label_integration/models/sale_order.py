from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lead_id = fields.Many2one('crm.lead', string="Lead")

    # EP-Online fields
    energy_label = fields.Char(string="Energy Label")
    energy_index = fields.Float(string="Energy Index")
    label_type = fields.Char(string="Label Type")
    label_valid_until = fields.Date(string="Label Validity End")
    thermal_area = fields.Float(string="Thermal Area (m²)")

    # BAG fields
    bag_street = fields.Char(string="BAG Street")
    bag_city = fields.Char(string="BAG City")
    bag_address_id = fields.Char(string="BAG Address Object ID")
    bag_usage = fields.Char(string="BAG Usage")
    bag_construction_year = fields.Integer(string="BAG Construction Year")
    bag_area = fields.Float(string="BAG Area (m²)")

    # Other fields
    co2_emissions = fields.Float(string="CO₂ Emissions (kg/year)")
    raw_api_response = fields.Text(string="API Raw Response")

    # Manual override flag
    energy_data_manual_override = fields.Boolean(string='Manual Override of Energy Data')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            lead_id = vals.get('lead_id') or self.env.context.get('default_lead_id') or self.env.context.get('default_opportunity_id')
            if lead_id:
                vals['lead_id'] = lead_id

        orders = super().create(vals_list)

        for order, vals in zip(orders, vals_list):
            if order.lead_id and not vals.get('energy_data_manual_override'):
                lead = order.lead_id
                order.write({
                    'energy_label': lead.ep_energy_label,
                    'energy_index': lead.ep_energy_index,
                    'label_type': lead.ep_label_type,
                    'label_valid_until': lead.ep_validity_end,
                    'thermal_area': lead.ep_thermische_oppervlakte,
                    'bag_street': lead.bag_street,
                    'bag_city': lead.bag_city,
                    'bag_address_id': lead.bag_verblijfsobject_id,
                    'bag_usage': lead.bag_usage,
                    'bag_construction_year': lead.bag_construction_year,
                    'bag_area': lead.bag_oppervlakte,
                    'co2_emissions': lead.carbon_emissions,
                    'raw_api_response': lead.api_raw_response,
                })
        return orders

    def _notify_user(self, title, message, notif_type='success'):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notif_type,
                'sticky': False,
            }
        }

    def action_test_ep(self):
        try:
            ep_data = self.env['ep.online.api.client'].fetch_by_address(
                self.partner_id.zip, self.partner_id.huisnummer,
                self.partner_id.huisletter, self.partner_id.huisnummertoevoeging)
            self.energy_label = ep_data.get('energielabel')
            self.energy_index = ep_data.get('energieindex')
            self.label_type = ep_data.get('labelType')
            self.label_valid_until = ep_data.get('geldigheidsdatum')
            self.thermal_area = ep_data.get('thermische_oppervlakte')
            self.co2_emissions = ep_data.get('CO2Uitstoot')
            return self._notify_user(_('EP-Online Test'), _('EP-Online data fetched successfully.'))
        except Exception as e:
            raise UserError(_('EP-Online API test failed: %s') % e)

    def action_test_bag(self):
        try:
            bag_data = self.env['bag.api.client'].fetch_address(
                self.partner_id.zip, self.partner_id.huisnummer,
                self.partner_id.huisletter, self.partner_id.huisnummertoevoeging)
            adres = bag_data.embedded.adressen[0]
            self.bag_street = adres.openbareRuimteNaam
            self.bag_city = adres.woonplaatsNaam
            self.bag_address_id = adres.adresseerbaarObjectIdentificatie
            self.bag_usage = ', '.join(adres.gebruiksdoelen or [])
            self.bag_construction_year = int(adres.oorspronkelijkBouwjaar[0]) if adres.oorspronkelijkBouwjaar else None
            self.bag_area = adres.oppervlakte
            return self._notify_user(_('BAG Test'), _('BAG data fetched successfully.'))
        except Exception as e:
            raise UserError(_('BAG API test failed: %s') % e)

    def action_fetch_all_data(self):
        self.action_test_bag()
        self.action_test_ep()
        return self._notify_user(_('Data Fetch'), _('EP-Online and BAG data fetched successfully.'))
