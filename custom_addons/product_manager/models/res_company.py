from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    sales5_client_id = fields.Char("Sales5 Client ID")
    sales5_client_secret = fields.Char("Sales5 Client Secret")
    sales5_api_token = fields.Char("Sales5 API Token")
    sales5_refresh_token = fields.Char("Sales5 Refresh Token")
    sales5_token_expires_at = fields.Float("Sales5 Token Expiry Timestamp")
    
    
    
    # usage:
    # company = request.env.company
    # token = company.sales5_api_token
