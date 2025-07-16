from odoo.tests.common import TransactionCase

class TestSiteVisitModule(TransactionCase):
    def test_create_visit_with_image_and_points(self):
        partner = self.env['res.partner'].create({'name': 'Test Customer'})
        category = self.env['site.inspection.category'].search([], limit=1)
        component = self.env['site.inspection.component'].search([('category_id', '=', category.id)], limit=1)

        visit = self.env['site.visit'].create({
            'name': 'Test Visit',
            'customer_id': partner.id,
            'visit_date': '2025-01-01'
        })

        image = self.env['site.visit.image'].create({
            'visit_id': visit.id,
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA',
            'category_id': category.id,
            'component_id': component.id,
            'note': 'Test image upload'
        })

        self.assertTrue(image.point_ids, "Auto-created inspection points failed")