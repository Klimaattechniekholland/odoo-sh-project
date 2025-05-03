from odoo import http
from odoo.http import request

class AIAssistantController(http.Controller):
    @http.route("/ai_assistant/ask", type="json", auth="user")
    def ask(self, prompt, model="gpt"):
        if not request.env.user.has_group("base.group_system"):
            return {"error": "Unauthorized"}
        response = request.env["ai.assistant"].sudo().call_ai(prompt, model)
        return {"response": response}
