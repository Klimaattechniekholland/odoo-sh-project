from odoo import http
from odoo.addons.product_manager.utils import token_required
from odoo.http import request


class Sales5ApiController(http.Controller):

    @http.route('/api/sales5/import', type='json', auth='public', methods=['POST'], csrf=False)
    @token_required
    def import_sales5_data(self, **kwargs):
        sales5_data = kwargs.get('data')

        if not sales5_data:
            return {"status": "error", "message": "Missing Sales5 data"}

        try:
            request.env['sales5.data'].sudo().import_or_update_sales5(sales5_data)
            return {"status": "success", "message": "Sales5 data processed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
