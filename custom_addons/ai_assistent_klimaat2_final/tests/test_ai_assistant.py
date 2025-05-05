import json
from odoo.tests.common import TransactionCase, HttpCase

class TestAIAssistant(HttpCase, TransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self.env.ref('base.user_root')
        self.url = '/ai_assistant/prompt'

    def test_prompt_route_unauthorized(self):
        res = self.url_open(self.url, data=json.dumps({'prompt': 'Hallo', 'model': 'res.partner'}))
        self.assertEqual(res.status_code, 401)

    def test_prompt_route_authorized(self):
        self.authenticate(self.user.login, 'odoo')
        data = {'prompt': 'Test', 'model': 'res.partner', 'res_id': None}
        res = self.url_open(self.url, data=json.dumps(data))
        self.assertEqual(res.status_code, 200)
        body = json.loads(res.body)
        self.assertIn('antwoord', body)
