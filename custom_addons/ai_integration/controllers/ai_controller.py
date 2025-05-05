from odoo import http
from odoo.http import request

class AIIntegrationController(http.Controller):
    @http.route('/ai_integration/ask', type='json', auth='user', methods=['POST'], csrf=False)
    def ask(self, prompt):
        service = request.env['ai_integration.service'].sudo()
        answer = service.ask_ai(prompt)
        return answer
