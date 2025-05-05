import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class AIAssistantController(http.Controller):
    @http.route('/ai_assistant/prompt', type='json', auth='user', methods=['POST'], csrf=True)
    def handle_prompt(self, prompt, model, res_id=None):
        if not request.env.user.has_group('base.group_system'):
            raise AccessError("Je hebt geen toegang tot de AI-assistent.")
        try:
            assistant = request.env['ai.assistant'].sudo()
            enriched = f"Context: model={model}, id={res_id} -- Vraag: {prompt}"
            antwoord = assistant.call_ai(enriched)
            return {'antwoord': antwoord}
        except Exception as e:
            _logger.exception('AI call mislukt')
            return {'error': 'AI-service niet beschikbaar, probeer later opnieuw.'}
