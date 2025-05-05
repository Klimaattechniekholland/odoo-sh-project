from odoo.tests.common import TransactionCase

class TestPromptWizard(TransactionCase):
    def test_wizard_action(self):
        wizard = self.env['x_ai_prompt_wizard'].create({
            'prompt': 'Hallo',
            'model': 'res.partner',
            'res_id': None,
        })
        action = wizard.action_send()
        self.assertEqual(action.get('type'), 'ir.actions.client')
        self.assertIn('message', action.get('params'))
