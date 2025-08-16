# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_proposal_quotation = fields.Boolean(
        string="Is Proposal",
        default=False,
        help="If checked, this sale order is a proposal quotation derived from a main quotation."
    )
    parent_quotation_id = fields.Many2one(
        "sale.order",
        string="Parent Quotation",
        domain=[('is_proposal_quotation', '=', False)],
        ondelete="cascade",
    )
    proposal_state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='draft', string="Proposal Status", tracking=True)

    proposal_quotation_ids = fields.One2many(
        "sale.order", "parent_quotation_id",
        string="Proposals",
        domain=[('is_proposal_quotation', '=', True)]
    )

    has_proposals = fields.Boolean(
        compute="_compute_has_proposals",
        string="Has Proposals"
    )
    proposal_count = fields.Integer(
        compute="_compute_proposal_count",
        string="Proposal Count"
    )

    @api.depends('proposal_quotation_ids')
    def _compute_has_proposals(self):
        for order in self:
            order.has_proposals = bool(order.proposal_quotation_ids)

    @api.depends('proposal_quotation_ids')
    def _compute_proposal_count(self):
        for order in self:
            order.proposal_count = len(order.proposal_quotation_ids)
