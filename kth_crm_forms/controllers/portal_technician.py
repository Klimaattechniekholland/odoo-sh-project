# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class TechnicianReportPortal(http.Controller):

    @http.route(['/my/technician_report/<int:lead_id>'], type='http', auth='user', website=True)
    def technician_report_form(self, lead_id, **kwargs):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.not_found()
        return request.render('kth_crm_forms.portal_technician_report', {'lead': lead})

    @http.route(['/my/technician_report/submit/<int:lead_id>'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def technician_report_submit(self, lead_id, **post):
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.not_found()

        lead.sudo().write({
            'report_date': post.get('report_date'),
            'report_fullname': post.get('report_fullname'),
            'report_address': post.get('report_address'),
            'component': post.get('component'),
            'defect_type': post.get('defect_type'),
            'defect_code': post.get('defect_code'),
            'intensity': post.get('intensity'),
            'score': post.get('score'),
        })

        # Handle file uploads
        files = request.httprequest.files.getlist('photos')
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': file.read().encode('base64'),
                'res_model': 'crm.lead',
                'res_id': lead.id,
                'mimetype': file.content_type,
            })
            lead.photo_ids = [(4, attachment.id)]

        return request.render('kth_crm_forms.portal_technician_success', {'lead': lead})
