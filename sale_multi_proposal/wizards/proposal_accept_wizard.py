# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError

class ProposalAcceptWizard(models.TransientModel):
    _name = "sale.proposal.accept.wizard"
    _description = "Accept Proposal Wizard"

    proposal_id = fields.Many2one("sale.order", required=True, domain=[('is_proposal_quotation', '=', True)])
    convert_to_main = fields.Boolean(string="Convert to Main Quotation", default=True)

    def action_confirm(self):
        self.ensure_one()
        proposal = self.proposal_id
        if proposal.state not in ('draft', 'sent'):
            raise UserError(_('Only proposals in Draft or Sent can be accepted.'))

        proposal.write({'proposal_state': 'accepted'})

        if self.convert_to_main:
            parent = proposal.parent_quotation_id
            if not parent:
                raise UserError(_('This proposal has no parent to replace.'))

            svc = self.env['sale.proposal.service']
            svc.duplicate_order_lines(proposal, parent)
            parent.write({
                'partner_id': proposal.partner_id.id,
                'pricelist_id': proposal.pricelist_id.id,
                'payment_term_id': proposal.payment_term_id.id or False,
                'fiscal_position_id': proposal.fiscal_position_id.id or False,
                'validity_date': proposal.validity_date,
                'client_order_ref': proposal.client_order_ref,
            })
        return {'type': 'ir.actions.act_window_close'}
