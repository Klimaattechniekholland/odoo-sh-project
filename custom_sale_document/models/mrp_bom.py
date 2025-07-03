from odoo import fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    marketing_text = fields.Html(string='Marketing Text')
    marketing_image = fields.Binary(string='Marketing Image')
    is_visible_in_quote = fields.Boolean(string='Visible in Quote')

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    show_in_quote = fields.Boolean(string='Show in Quote')
    component_price = fields.Monetary(
        string='Component Price',
        related='product_id.list_price',
        currency_field='product_id.currency_id',
        readonly=True
    )