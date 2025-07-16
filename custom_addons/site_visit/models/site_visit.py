from odoo import models, fields

class SiteVisit(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'site.visit'
    _description = 'Site Visit'
    
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    technician_id = fields.Many2one('res.users', string='Technician')
    image_ids = fields.One2many('site.visit.image', 'visit_id', string='Images')

    name = fields.Char(string='Visit Reference', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('site.visit'))
    visit_date = fields.Date(track_visibility='onchange',string='Visit Date', default=fields.Date.today)
    has_heatpump = fields.Boolean(string='Heat Pump Present', store=True)
    has_airco = fields.Boolean(string='Airco Present', store=True)
    has_battery = fields.Boolean(string='Battery Present', store=True)
    has_cv = fields.Boolean(string='CV Present', store=True)
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')

    def action_view_images_by_category(self, category):
        return {
            'type': 'ir.actions.act_window',
            'name': f'{category.capitalize()} Photos',
            'res_model': 'site.visit.image',
            'view_mode': 'kanban,tree,form',
            'domain': [('visit_id', '=', self.id), ('category', '=', category)],
            'context': {'default_visit_id': self.id, 'default_category': category}
        }

    def action_send_report_email(self):
        template = self.env.ref('site_visit.email_template_site_visit')
        for visit in self:
            template.send_mail(visit.id, force_send=True)
    