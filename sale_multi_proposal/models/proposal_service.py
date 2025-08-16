# -*- coding: utf-8 -*-
from odoo import api, models

class ProposalService(models.AbstractModel):
    _name = "sale.proposal.service"
    _description = "Service helpers for proposal duplication"

    @api.model
    def get_default_values_from_order(self, order):
        """Return dict of values to initialize a proposal from a main order."""
        return {
            'company_id': order.company_id.id,
            'partner_id': order.partner_id.id,
            'partner_invoice_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'pricelist_id': order.pricelist_id.id,
            'currency_id': order.currency_id.id,
            'payment_term_id': order.payment_term_id.id or False,
            'fiscal_position_id': order.fiscal_position_id.id or False,
            'validity_date': order.validity_date,
            'client_order_ref': order.client_order_ref,
            'team_id': order.team_id.id or False,
            'user_id': order.user_id.id or False,
            'origin': order.name,
            #'warehouse_id': order.warehouse_id.id or False,
        }

    @api.model
    def duplicate_order_lines(self, from_order, to_order):
        """Copy lines from source order into target order.

        - If target is a quotation (draft/sent): clear lines (unlink) then write proposal lines.
        - If target is confirmed: DO NOT unlink. Set qty=0 on existing lines (non-display),
          then append proposal lines.
        """
        new_lines_vals = []
        for line in from_order.order_line:
            new_lines_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'display_type': line.display_type,
            }))

        if to_order.state in ('draft', 'sent'):
            to_order.order_line.unlink()
            to_order.write({'order_line': new_lines_vals})
        else:
            for l in to_order.order_line:
                if not l.display_type:
                    l.write({'product_uom_qty': 0})
            to_order.write({'order_line': new_lines_vals})

        return to_order
