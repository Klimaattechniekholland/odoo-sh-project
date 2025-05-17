# -*- coding: utf-8 -*-
# from odoo import http


# class EnergyLabelIntegration(http.Controller):
#     @http.route('/energy_label_integration/energy_label_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/energy_label_integration/energy_label_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('energy_label_integration.listing', {
#             'root': '/energy_label_integration/energy_label_integration',
#             'objects': http.request.env['energy_label_integration.energy_label_integration'].search([]),
#         })

#     @http.route('/energy_label_integration/energy_label_integration/objects/<model("energy_label_integration.energy_label_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('energy_label_integration.object', {
#             'object': obj
#         })

