from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    house_photo = fields.Binary(string='House Photo')
    system_description = fields.Text(string='System Description')
    subsidy_amount = fields.Float(string='Subsidy Amount')
    meldcode = fields.Char(string='Meldcode')
    kit_bom_ids = fields.Many2many(
        'mrp.bom',
        compute='_compute_kit_boms',
        string='Kits',
        store=False
    )
    invoice_variant = fields.Selection(
        [('installation', 'Installation'), ('service', 'Service')],
        string='Invoice Variant',
        default='installation',
        required=True,
    )
    contract_duration_months = fields.Integer(string='Contract Duration (Months)', default=12)
    payment_frequency = fields.Selection(
        [('monthly', 'Monthly'), ('yearly', 'Yearly')],
        string='Payment Frequency',
        default='monthly'
    )
    require_signature = fields.Boolean(string='Require Digital Signature')
    qr_code = fields.Binary(string='QR Code')

    def _compute_kit_boms(self):
        for move in self:
            kit_boms = self.env['mrp.bom']
            for line in move.invoice_line_ids:
                product = line.product_id
    
                # BOMs on product variant
                product_boms = product.bom_ids.filtered(
                    lambda b: b.type == 'phantom' and b.company_id.id == move.company_id.id
                )
    
                # BOMs on product template
                template_boms = product.product_tmpl_id.bom_ids.filtered(
                    lambda b: b.type == 'phantom' and b.company_id.id == move.company_id.id
                )
    
                kit_boms |= product_boms | template_boms
    
            move.kit_bom_ids = kit_boms