from odoo import models, fields, api
from odoo.exceptions import UserError

class AIPromptWizard(models.TransientModel):
    _name = 'ai.prompt.wizard'
    _description = 'Wizard for AI Prompts'
    prompt = fields.Text(string='Vraag aan AI', required=True)
    model = fields.Char(string='Context Model', readonly=True)
    res_id = fields.Integer(string='Context Record ID', readonly=True)

    def action_send(self):
        assistant = self.env['ai.assistant'].sudo()
        enriched = f"Context: model={self.model}, id={self.res_id} — Vraag: {self.prompt}"
        try:
            antwoord = assistant.call_ai(enriched)
        except UserError as e:
            raise e
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'AI Antwoord',
                'message': antwoord,
                'sticky': False,
            }
        }
