from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderProposition(models.Model):
    """Alternative proposal attached to a sale order."""

    _name = 'sale.order.proposition'
    _description = 'Sale Order Proposition'
    _order = 'sequence, id'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Quotation',
        required=True,
        ondelete='cascade',
        help='The sale order to which this proposition belongs.'
    )
    name = fields.Char(required=True, string='Proposition Name')
    note = fields.Text(string='Internal Note')
    sequence = fields.Integer(default=10, help='Display order of the proposition within the sale order.')
    line_ids = fields.One2many(
        'sale.order.proposition.line',
        'proposition_id',
        string='Proposition Lines',
        copy=True
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('selected', 'Selected'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
        string='Status'
    )
    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        compute='_compute_amounts',
        store=True,
    )
    amount_tax = fields.Monetary(
        string='Taxes',
        compute='_compute_amounts',
        store=True,
    )
    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amounts',
        store=True,
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        store=True,
        readonly=True,
        string='Currency'
    )

    @api.depends('line_ids.price_subtotal', 'line_ids.price_tax')
    def _compute_amounts(self):
        """Compute monetary totals for each proposition.

        Uses ``price_subtotal`` and ``price_tax`` from the lines to
        calculate untaxed, tax and total amounts.  Follows the pattern
        for computed fields from the ORM documentation【710326666742125†L3305-L3333】.
        """
        for prop in self:
            untaxed = sum(prop.line_ids.mapped('price_subtotal'))
            tax = sum(prop.line_ids.mapped('price_tax'))
            prop.amount_untaxed = untaxed
            prop.amount_tax = tax
            prop.amount_total = untaxed + tax

    def action_confirm_proposition(self):
        """Confirm this proposition and copy its lines into the sale order.

        When a proposition is confirmed, it marks itself as selected,
        assigns itself to the sale order's selected_proposition_id and
        replaces any existing ``sale.order.line`` records on the order
        with new lines copied from this proposition.  It then calls
        ``action_confirm`` on the sale order to proceed with the usual
        confirmation workflow.
        """
        for prop in self:
            if prop.state != 'draft':
                continue
            sale_order = prop.sale_order_id
            # Remove existing sale order lines
            sale_order.order_line.unlink()
            # Copy proposition lines into sale order lines
            for line in prop.line_ids:
                sale_order.order_line.create({
                    'order_id': sale_order.id,
                    'product_id': line.product_id.id,
                    'name': line.name or line.product_id.display_name,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'tax_id': [(6, 0, line.tax_id.ids)],
                    'discount': line.discount,
                })
            # Set selected proposition on the order
            sale_order.selected_proposition_id = prop.id
            prop.state = 'selected'
            # Confirm the sale order normally
            sale_order.action_confirm()


class SaleOrderPropositionLine(models.Model):
    """Line of a sale order proposition.

    Mirrors many of the fields on ``sale.order.line`` but remains
    independent until a proposition is confirmed.
    """

    _name = 'sale.order.proposition.line'
    _description = 'Sale Order Proposition Line'
    _order = 'proposition_id, id'

    proposition_id = fields.Many2one(
        'sale.order.proposition',
        string='Proposition',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('sale_ok', '=', True)]
    )
    name = fields.Char(
        string='Description',
        help='Description of the product or service being sold.'
    )
    product_uom_qty = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        default=1.0,
        required=True
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        digits='Product Price'
    )
    tax_id = fields.Many2many(
        'account.tax',
        string='Taxes',
        domain=[('type_tax_use', 'in', ('sale', 'all'))]
    )
    discount = fields.Float(
        string='Discount (%)',
        digits='Discount',
        default=0.0
    )
    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_price',
        store=True
    )
    price_tax = fields.Monetary(
        string='Tax Amount',
        compute='_compute_price',
        store=True
    )
    currency_id = fields.Many2one(
        related='proposition_id.currency_id',
        store=True,
        readonly=True,
        string='Currency'
    )

    @api.depends('product_uom_qty', 'price_unit', 'discount', 'tax_id')
    def _compute_price(self):
        """Compute subtotal and tax for each proposition line."""
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # Compute taxes using account.tax compute_all method
            taxes_res = line.tax_id.compute_all(
                price,
                currency=line.currency_id,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=line.proposition_id.sale_order_id.partner_id,
            ) if line.tax_id else {
                'total_excluded': price * line.product_uom_qty,
                'total_included': price * line.product_uom_qty,
            }
            line.price_subtotal = taxes_res['total_excluded']
            line.price_tax = taxes_res['total_included'] - taxes_res['total_excluded']