from odoo import models, fields


class BagLookupHistory(models.Model):
	_name = 'bag.lookup.history'
	_description = 'BAG Lookup History'
	
	name = fields.Char(string = "Name", required = True)
	date = fields.Datetime(string = "Date")
	
	partner_id = fields.Many2one('res.partner', string = "Partner")
	result_status = fields.Selection(
		[
			('success', 'Success'),
			('failure', 'Failure'),
			('fallback', 'Fallback')
			], string = "Result Status"
		)
	lookup_date = fields.Datetime(string = "Lookup Date", default = fields.Datetime.now)
	fallback_message = fields.Text(string = "Fallback Message")
