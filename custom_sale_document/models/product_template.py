from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quote_visibility = fields.Selection([
        ('visible', 'Visible in Orders'),
        ('kit_only', 'Kit Components Only'),
        ('none', 'Not Visible in Orders'),
    ], string='Order Line Visibility', default='visible')
