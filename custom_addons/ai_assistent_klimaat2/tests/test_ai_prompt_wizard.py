import json
from odoo.tests.common import TransactionCase, HttpCase

class TestPromptWizard(HttpCase, TransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self.env.ref('base.user_root')
        self.url = '/ai_assistant/prompt'

    def test_wizard_call(self):
        wizard = self.env['ai.prompt.wizard'].create({
            'prompt': 'Hallo',
            'model': 'res.partner',
            'res_id': None,
        })
        action = wizard.action_send()
        self.assertEqual(action.get('type'), 'ir.actions.client')
