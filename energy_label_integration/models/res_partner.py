# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    huisnummer = fields.Char(string="House Number")
    huisletter = fields.Char(string="House Letter")
    huisnummertoevoeging = fields.Char(string="Addition")
