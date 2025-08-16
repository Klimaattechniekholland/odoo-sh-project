# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmLeadTechnician(models.Model):
    _inherit = "crm.lead"

    report_date = fields.Date("Report Date / Datum")
    report_fullname = fields.Char("Technician Fullname")
    report_address = fields.Char("Location Address / Adres")
    component = fields.Char("Onderdeel / Component")
    defect_type = fields.Char("Soortgebrek / Type of Defect")
    defect_code = fields.Char("Code")
    intensity = fields.Selection([
        ('low', 'Low / Laag'),
        ('medium', 'Medium / Gemiddeld'),
        ('high', 'High / Hoog'),
    ], string="Intensiteit / Intensity")
    score = fields.Float("Score")
    photo_ids = fields.Many2many(
        'ir.attachment', 'lead_technician_photo_rel', 'lead_id', 'attachment_id',
        string="Site Photos",
        help="Photos taken on site during technician visit"
    )

    def action_open_technician_portal(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/my/technician_report/{self.id}',
            'target': 'new',
        }
