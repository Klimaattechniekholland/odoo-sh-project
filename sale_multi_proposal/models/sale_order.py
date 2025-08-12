"""Extension of sale.order to support multiple proposals.

Adds one2many and many2one fields linking sale orders with
propositions and exposes helper methods for computing totals based
on a selected proposition.  The ``selected_proposition_id`` field
references the proposition that has been chosen by the customer.
"""

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    proposition_ids = fields.One2many(
        'sale.order.proposition',
        'sale_order_id',
        string='Propositions',
        copy=True
    )
    selected_proposition_id = fields.Many2one(
        'sale.order.proposition',
        string='Selected Proposition',
        copy=False,
        help='If set, indicates which proposition has been chosen '
             'and copied into this sale order as the official quotation.'
    )

    @api.onchange('proposition_ids')
    def _onchange_proposition_ids(self):
        """When propositions change, clear selected proposition if it's gone."""
        for order in self:
            if order.selected_proposition_id not in order.proposition_ids:
                order.selected_proposition_id = False