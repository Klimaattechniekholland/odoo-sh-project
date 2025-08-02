from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_pricing_ids = fields.One2many(
        'product.pricing',
        'product_pricing_id',
        string='Pricing Details'
    )
