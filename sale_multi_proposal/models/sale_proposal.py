from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Recursive relationship for proposal quotations
    parent_quotation_id = fields.Many2one(
        'sale.order',
        string='Parent Quotation',
        help="The main quotation this proposal belongs to",
        ondelete='cascade'
    )
    
    proposal_quotation_ids = fields.One2many(
        'sale.order',
        'parent_quotation_id',
        string='Proposal Quotations',
        help="Proposal quotations for this main quotation"
    )
    
    is_proposal_quotation = fields.Boolean(
        string='Is Proposal Quotation',
        default=False,
        help="True if this quotation is a proposal, not the main quotation"
    )
    
    proposal_state = fields.Selection([
        ('draft', 'Draft'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ], 
        string='Proposal State',
        default='draft',
        help="State of the proposal quotation"
    )
    
    has_proposals = fields.Boolean(
        string='Has Proposals',
        compute='_compute_has_proposals',
        store=True,
        help="True if this quotation has proposal quotations"
    )
    
    proposal_count = fields.Integer(
        string='Proposal Count',
        compute='_compute_proposal_count',
        help="Number of proposal quotations"
    )

    @api.depends('proposal_quotation_ids')
    def _compute_has_proposals(self):
        for order in self:
            order.has_proposals = bool(order.proposal_quotation_ids)

    @api.depends('proposal_quotation_ids')
    def _compute_proposal_count(self):
        for order in self:
            order.proposal_count = len(order.proposal_quotation_ids)

    @api.model
    def create(self, vals):
        """Ensure proposal quotations start in draft state and have proper naming"""
        if vals.get('is_proposal_quotation'):
            if not vals.get('proposal_state'):
                vals['proposal_state'] = 'draft'
            # Auto-generate name for proposal quotations
            if vals.get('parent_quotation_id') and not vals.get('name', '').startswith('New'):
                parent = self.browse(vals['parent_quotation_id'])
                proposal_count = len(parent.proposal_quotation_ids) + 1
                vals['name'] = f"{parent.name} - Proposal {proposal_count}"
        return super().create(vals)

    def write(self, vals):
        """Prevent modification of selected/rejected proposals"""
        if 'proposal_state' not in vals:
            for order in self:
                if order.is_proposal_quotation and order.proposal_state in ('selected', 'rejected'):
                    # Allow certain fields to be modified even for finalized proposals
                    allowed_fields = {'name', 'note', 'client_order_ref', 'validity_date'}
                    if set(vals.keys()) - allowed_fields:
                        raise UserError(_(
                            "Cannot modify %s proposal quotations. Only name, note, client reference and validity date can be changed."
                        ) % order.proposal_state)
        return super().write(vals)

    def unlink(self):
        """Prevent deletion of selected proposals (for traceability)"""
        selected_proposals = self.filtered(
            lambda o: o.is_proposal_quotation and o.proposal_state == 'selected'
        )
        if selected_proposals:
            raise UserError(_(
                "Cannot delete selected proposal quotations. They are kept for traceability purposes."
            ))
        return super().unlink()

    def action_select_proposal_quotation(self):
        """
        Select this proposal quotation:
        1. Copy all lines from this proposal to the parent quotation
        2. Mark all other proposal quotations as rejected
        3. Mark this proposal quotation as selected
        4. Optionally copy quotation-level data (terms, validity, etc.)
        """
        self.ensure_one()
        
        if not self.is_proposal_quotation:
            raise UserError(_("This action can only be performed on proposal quotations."))
        
        if self.proposal_state != 'draft':
            raise UserError(_("Only draft proposals can be selected."))
        
        if not self.parent_quotation_id:
            raise UserError(_("Proposal quotation must have a parent quotation."))
        
        # 1. Clear existing lines from parent quotation (optional - you can modify this)
        # self.parent_quotation_id.order_line.unlink()
        
        # 2. Copy all lines from this proposal to the parent quotation
        for line in self.order_line:
            line_data = self._prepare_selected_line_data(line)
            line_data['order_id'] = self.parent_quotation_id.id
            self.env['sale.order.line'].create(line_data)
        
        # 3. Copy important quotation-level data to parent
        self._copy_quotation_data_to_parent()
        
        # 4. Mark all other proposal quotations on the parent as rejected
        other_proposals = self.parent_quotation_id.proposal_quotation_ids.filtered(
            lambda o: o.id != self.id and o.proposal_state == 'draft'
        )
        other_proposals.write({'proposal_state': 'rejected'})
        
        # 5. Mark this proposal as selected
        self.proposal_state = 'selected'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Proposal Selected'),
                'message': _('The proposal quotation has been selected and its content copied to the main quotation.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _prepare_selected_line_data(self, line):
        """Prepare data for copying proposal line to parent quotation"""
        line_data = line.copy_data()[0]
        # Remove id and order_id to create new line
        line_data.pop('id', None)
        line_data.pop('order_id', None)
        return line_data

    def _copy_quotation_data_to_parent(self):
        """Copy relevant quotation data to parent when selected"""
        parent = self.parent_quotation_id
        # Copy selected quotation-level data
        update_vals = {}
        
        # You can customize which fields to copy
        if self.validity_date and self.validity_date != parent.validity_date:
            update_vals['validity_date'] = self.validity_date
        
        if self.payment_term_id and self.payment_term_id != parent.payment_term_id:
            update_vals['payment_term_id'] = self.payment_term_id.id
        
        if self.incoterm_id and self.incoterm_id != parent.incoterm_id:
            update_vals['incoterm_id'] = self.incoterm_id.id
        
        # Add note about selected proposal
        if self.note:
            note_addition = f"\n\nSelected from Proposal: {self.name}\n{self.note}"
            update_vals['note'] = (parent.note or '') + note_addition
        
        if update_vals:
            parent.write(update_vals)

    def action_create_proposal_quotation(self):
        """Create a new proposal quotation based on this quotation"""
        self.ensure_one()
        
        if self.is_proposal_quotation:
            raise UserError(_("Cannot create proposals from proposal quotations."))
        
        if self.state not in ('draft', 'sent'):
            raise UserError(_("Can only create proposals from draft or sent quotations."))
        
        # Create proposal quotation
        proposal_data = self._prepare_proposal_quotation_data()
        proposal_quotation = self.create(proposal_data)
        
        # Copy lines to proposal quotation
        for line in self.order_line:
            line_data = line.copy_data()[0]
            line_data['order_id'] = proposal_quotation.id
            self.env['sale.order.line'].create(line_data)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Proposal Quotation'),
            'res_model': 'sale.order',
            'res_id': proposal_quotation.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _prepare_proposal_quotation_data(self):
        """Prepare data for creating a proposal quotation"""
        proposal_count = len(self.proposal_quotation_ids) + 1
        return {
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'pricelist_id': self.pricelist_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'warehouse_id': self.warehouse_id.id,
            'parent_quotation_id': self.id,
            'is_proposal_quotation': True,
            'proposal_state': 'draft',
            'name': f"{self.name} - Proposal {proposal_count}",
            'note': self.note,
            'payment_term_id': self.payment_term_id.id if self.payment_term_id else False,
            'fiscal_position_id': self.fiscal_position_id.id if self.fiscal_position_id else False,
            'incoterm_id': self.incoterm_id.id if self.incoterm_id else False,
            'validity_date': self.validity_date,
            'client_order_ref': self.client_order_ref,
        }

    def action_view_proposals(self):
        """Smart button action to view all proposals"""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [('parent_quotation_id', '=', self.id)]
        action['context'] = {
            'default_parent_quotation_id': self.id,
            'default_is_proposal_quotation': True,
        }
        if self.proposal_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.proposal_quotation_ids[0].id
        return action

    @api.constrains('parent_quotation_id', 'is_proposal_quotation')
    def _check_proposal_consistency(self):
        """Ensure proposal quotation consistency"""
        for order in self:
            if order.is_proposal_quotation and not order.parent_quotation_id:
                raise ValidationError(_("Proposal quotations must have a parent quotation."))
            if not order.is_proposal_quotation and order.parent_quotation_id:
                raise ValidationError(_("Non-proposal quotations cannot have a parent quotation."))
            if order.parent_quotation_id and order.parent_quotation_id.is_proposal_quotation:
                raise ValidationError(_("Proposal quotations cannot have other proposals as parents."))

    @api.constrains('state', 'is_proposal_quotation')
    def _check_proposal_state_changes(self):
        """Prevent proposal quotations from being confirmed directly"""
        for order in self:
            if order.is_proposal_quotation and order.state not in ('draft', 'sent', 'cancel'):
                raise ValidationError(_(
                    "Proposal quotations cannot be confirmed directly. "
                    "Please select the proposal first to copy it to the main quotation."
                ))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_amount(self):
        """Standard computation - proposal quotations are handled at quotation level"""
        super()._compute_amount()