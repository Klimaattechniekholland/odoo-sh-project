from odoo.tests.common import TransactionCase

class TestSiteVisitEmail(TransactionCase):
    def test_send_email(self):
        visit = self.env['site.visit'].create({
            'name': 'Visit for Email Test',
            'customer_id': self.env['res.partner'].create({'name': 'Email Client', 'email': 'test@example.com'}).id,
            'visit_date': '2025-07-01'
        })
        template = self.env.ref('site_visit.email_template_site_visit')
        template.send_mail(visit.id, force_send=True)