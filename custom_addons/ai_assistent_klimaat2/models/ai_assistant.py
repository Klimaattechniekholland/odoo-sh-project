from odoo import models, fields, api
from odoo.exceptions import UserError
import requests

class AIAssistant(models.Model):
    _name = 'x_ai_assistant'
    _description = 'AI Developer Assistant'

    name = fields.Char(string='Naam', required=True)

    @api.model
    def call_ai(self, prompt: str) -> str:
        params = self.env['ir.config_parameter'].sudo()
        openai_key = params.get_param('ai_assistant.openai_key')
        gemini_key = params.get_param('ai_assistant.gemini_key')
        if openai_key:
            headers = {'Authorization': f'Bearer {openai_key}'}
            payload = {'model': 'gpt-4', 'messages': [{'role': 'user', 'content': prompt}]}
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)
            if response.status_code != 200:
                raise UserError(f'OpenAI error: {response.text}')
            return response.json()['choices'][0]['message']['content']
        elif gemini_key:
            headers = {'X-API-Key': gemini_key}
            payload = {'prompt': prompt}
            response = requests.post('https://gemini.api.url/v1/generate', headers=headers, json=payload)
            if response.status_code != 200:
                raise UserError(f'Gemini error: {response.text}')
            return response.json().get('result', '')
        else:
            raise UserError('Geen AI API-sleutel geconfigureerd.')
