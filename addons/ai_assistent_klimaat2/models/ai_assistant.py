from odoo import models, fields, api
import openai
import requests

class AIAssistant(models.Model):
    _name = "ai.assistant"
    _description = "AI Developer Assistent"

    name = fields.Char(string="Name")
    model = fields.Selection([("gpt", "GPT-4"), ("gemini", "Gemini")], default="gpt")
    prompt = fields.Text(string="Prompt")
    response = fields.Text(string="Response", readonly=True)

    @api.model
    def call_ai(self, prompt, model="gpt"):
        config = self.env["ai.assistant.config"].sudo().search([], limit=1)
        if model == "gpt":
            openai.api_key = config.gpt_api_key
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message["content"]
        elif model == "gemini":
            headers = {"Authorization": f"Bearer {config.gemini_api_key}"}
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )
            return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return "No response"
