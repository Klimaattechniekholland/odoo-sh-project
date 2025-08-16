# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_create_proposal(self):
        self.ensure_one()
        if self.is_proposal_quotation:
            raise UserError(_('You can only create proposals from a main quotation.'))

        proposal_count = self.proposal_count + 1
        name = f"{self.name} - Proposal {proposal_count}"

        service = self.env['sale.proposal.service']
        vals = service.get_default_values_from_order(self)
        vals.update({
            'is_proposal_quotation': True,
            'parent_quotation_id': self.id,
            'proposal_state': 'draft',
            'name': name,
        })

        proposal = self.env['sale.order'].create(vals)
        service.duplicate_order_lines(self, proposal)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Proposal Quotation'),
            'res_model': 'sale.order',
            'res_id': proposal.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_proposals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Proposals'),
            'res_model': 'sale.order',
            'view_mode': 'list,form,kanban',
            'domain': [('parent_quotation_id', '=', self.id), ('is_proposal_quotation', '=', True)],
        }

    def action_open_accept_wizard(self):
        self.ensure_one()
        if not self.is_proposal_quotation:
            raise UserError(_('Only proposal quotations can be accepted.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Accept Proposal'),
            'res_model': 'sale.proposal.accept.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_proposal_id': self.id},
        }
