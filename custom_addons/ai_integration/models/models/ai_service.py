import requests
from odoo import models
from odoo.exceptions import UserError

class AIService(models.AbstractModel):
    _name = 'ai_integration.service'
    _description = 'AI Service for LLM calls'

    def _get_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('ai_integration.api_key') or ''

    def ask_ai(self, prompt):
        api_key = self._get_api_key()
        if not api_key:
            raise UserError("AI API-key is niet ingesteld. Ga naar Instellingen > AI Integration om de sleutel in te voeren.")
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': 'gpt-4o-mini',
            'messages': [{'role': 'user', 'content': prompt}]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(f"Fout bij AI-aanroep: {e}")
        data = response.json()
        if 'choices' in data and data['choices']:
            return data['choices'][0]['message']['content']
        else:
            raise UserError('Ongeldige response van AI-provider')
