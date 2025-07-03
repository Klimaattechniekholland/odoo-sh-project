from odoo import fields, models

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

    def _compute_kit_boms(self):
        for order in self:
            boms = self.env['mrp.bom']
            for line in order.order_line:
                tmpl = line.product_id.product_tmpl_id
                bom = self.env['mrp.bom']._bom_find(product=tmpl, company_id=order.company_id.id, bom_type='phantom')
                if bom:
                    boms |= bom
            order.kit_bom_ids = boms