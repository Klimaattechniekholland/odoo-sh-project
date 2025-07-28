from odoo import models, fields


class Sales5LineData(models.Model):
	_name = 'sales5.line.data'
	_description = 'Sales5 Sales Order Record line item'
	
	order_id = fields.Char(string = "Order Reference", required = True)
	order_date = fields.Date(string = "Order Date")
	
	customer_id = fields.Many2one('res.partner', string = "Customer")
	customer_contact = fields.Char(string = "Contact Person")
	customer_email = fields.Char(string = "Customer Email")
	
	shipping_street = fields.Char(string = "Shipping Street")
	shipping_city = fields.Char(string = "Shipping City")
	shipping_postal_code = fields.Char(string = "Postal Code")
	shipping_country = fields.Char(string = "Country")
	
	total_before_tax = fields.Float(string = "Subtotal")
	tax_amount = fields.Float(string = "Tax Amount")
	total_amount = fields.Float(string = "Total Amount")
	
	currency = fields.Char(string = "Currency", default = "USD")
	payment_terms = fields.Char(string = "Payment Terms")
	expected_delivery_date = fields.Date(string = "Expected Delivery")
	
	status = fields.Selection(
		[
			('draft', 'Draft'),
			('confirmed', 'Confirmed'),
			('delivered', 'Delivered')
			], string = "Order Status", default = "draft"
		)
	
	sales5_ids = fields.Many2one('sales5.data', 'sales5_id')
