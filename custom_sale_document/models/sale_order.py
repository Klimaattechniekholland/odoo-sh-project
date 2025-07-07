from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    house_photo = fields.Binary(
        string='House Photo',
        help='Optional image of the client house for reference.'
    )
    system_description = fields.Text(
        string='System Description',
        help='Custom description of the installed system.'
    )
    subsidy_amount = fields.Float(string='Subsidy Amount')
    meldcode = fields.Char(string='Meldcode')
    kit_bom_ids = fields.Many2many(
        'mrp.bom',
        compute='_compute_kit_boms',
        string='Kits',
        help='Kits detected from order lines with kit BOMs.',
        store=False
    )
    contract_duration_months = fields.Integer(
        string='Contract Duration (Months)',
        default=12
    )
    payment_frequency = fields.Selection(
        [('monthly', 'Monthly'), ('yearly', 'Yearly')],
        string='Payment Frequency',
        default='monthly'
    )
    require_signature = fields.Boolean(string='Require Digital Signature')

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'house_photo': self.house_photo,
            'system_description': self.system_description,
            'subsidy_amount': self.subsidy_amount,
            'meldcode': self.meldcode,
            'contract_duration_months': self.contract_duration_months,
            'payment_frequency': self.payment_frequency,
            'require_signature': self.require_signature,
        })
        return invoice_vals

    @api.depends('order_line.product_id')
    def _compute_kit_boms(self):
        """Compute all BOMs of type 'phantom' (kits) for products in order lines."""
        for order in self:
            kit_boms = self.env['mrp.bom']
            _logger.info(f"Order: {order.name}")
            for line in order.order_line:
                product = line.product_id
                _logger.info(f"Checking product: {product.display_name} (ID: {product.id})")
    
                # BOMs on product
                product_boms = product.bom_ids.filtered(
                    lambda b: b.type == 'phantom' and b.company_id.id == order.company_id.id
                )
                _logger.info(f"Found {len(product_boms)} BOM(s) on product variant.")
    
                # BOMs on product template
                template_boms = product.product_tmpl_id.bom_ids.filtered(
                    lambda b: b.type == 'phantom' and b.company_id.id == order.company_id.id
                )
                _logger.info(f"Found {len(template_boms)} BOM(s) on product template.")
    
                kit_boms |= product_boms | template_boms
    
            _logger.info(f"Total kits found for order {order.name}: {len(kit_boms)}")
            order.kit_bom_ids = kit_boms