from odoo import models, fields

class AIUserContext(models.Model):
    _name = 'x_ai_user_context'
    _description = 'AI User Context'

    user_id = fields.Many2one('res.users', string='Gebruiker', default=lambda self: self.env.uid)
    session_uid = fields.Char(string='Sessienaam of ID')
    messages = fields.Text(string='Berichten JSON')
