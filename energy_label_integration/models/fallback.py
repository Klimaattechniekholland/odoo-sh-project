# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EnergyLabelFallback(models.Model):
    _name = 'energy.label.fallback'
    _description = 'Fallback for Missing Energy Label Data'
    _order = 'create_date desc'

    postcode = fields.Char(string="Postcode", required=True)
    huisnummer = fields.Char(string="House Number", required=True)
    huisletter = fields.Char(string="House Letter")
    huisnummertoevoeging = fields.Char(string="Number Addition")

    bag_verblijfsobject_id = fields.Char(string="BAG Verblijfsobject ID")
    ep_energy_label = fields.Char(string="Energy Label")
    ep_valid_until = fields.Date(string="Label Valid Until")

    note = fields.Text(string="Manual Note or Resolution")
    create_date = fields.Datetime(string="Created On", readonly=True)
    write_date = fields.Datetime(string="Last Updated", readonly=True)

    formatted_address = fields.Char(string="Formatted Address", compute="_compute_formatted_address", store=True)

    @api.depends('postcode', 'huisnummer', 'huisletter', 'huisnummertoevoeging')
    def _compute_formatted_address(self):
        for rec in self:
            addr = f"{rec.postcode or ''} {rec.huisnummer or ''}"
            if rec.huisletter:
                addr += rec.huisletter
            if rec.huisnummertoevoeging:
                addr += f"-{rec.huisnummertoevoeging}"
            rec.formatted_address = addr.strip()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.formatted_address or "Unnamed Fallback"))
        return result

    @classmethod
    def check_if_exists(cls, env, postcode, huisnummer, huisletter='', toevoeging=''):
        """ Utility to avoid duplicates """
        domain = [
            ('postcode', '=', postcode),
            ('huisnummer', '=', huisnummer),
            ('huisletter', '=', huisletter),
            ('huisnummertoevoeging', '=', toevoeging),
        ]
        return env['energy.label.fallback'].search(domain, limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'postcode' in vals:
                vals['postcode'] = vals['postcode'].replace(' ', '').upper()
        return super().create(vals_list)
