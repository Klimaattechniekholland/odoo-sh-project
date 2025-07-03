from odoo import api, fields, models

class ServiceContractWizard(models.TransientModel):
    _name = 'custom_sale_document.service_contract_wizard'
    _description = 'Service Contract Wizard'

    contract_duration = fields.Integer(string='Contract Duration (months)', required=True, default=12)
    frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Service Frequency', required=True, default='monthly')
    price = fields.Monetary(string='Price per Month', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    def action_print_contract(self):
        return self.env.ref('custom_sale_document.action_report_service_contract').report_action(self)