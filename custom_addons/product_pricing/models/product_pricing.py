from odoo import api, fields, models


class ProductTemplate(models.Model):
	_inherit = 'product.template'
	
	#
	# sales price => product_id.list_price
	# cost price => product_id.standard_price
	#
	# Calculate the cost price with our Discount
	# Cost = Sales price  * (1 - Discount)	#
	#
	# We normally calculate with mMargins not with Markup's
	# Margin = (SellingPrice - Cost) / SellingPrice
	# Markup = (Selling Price - Cost) / Cost
	# for the same amount of money, the markup is always higher
	# Margin 25%, Markup 33,333% gives the same earnings, default settings
	#
	# top-down
	# change product_supplier_sale_price or product_supplier_discount ==>
	#     change the Cost (standard_price)
	#     change the Sale price (list_price)
	#
	# change Cost (standard_price) ==>
	#     change the product_supplier_discount
	#     change the Sale price (list_price)
	#
	# change product_use_margin or product_margin or product_markup==>
	#     change the Sale price (list_price)
	#
	# change Sale price (list_price) ==>
	#     change the margin or markup
	
	supplier_sales_price = fields.Float(
		string = "Supplier Sales Price",
		digits = "Product Price",
		help = "Base price from the supplier before discount"
		)
	
	supplier_discount = fields.Float(
		string = "Discount %",
		digits = "Product Price",
		help = "Discount from supplier, e.g. 0.15 = 15%"
		)
	
	price_type = fields.Selection(
		[
			('margin', 'Margin'),
			('markup', 'Markup')
			],
		string = "Use",
		default = 'margin',
		required = True,
		help = "Toggle between Margin and Markup strategy"
		)
	
	is_price_type = fields.Boolean(
		string = "Result",
		compute = "_get_price_type",
		store = False
		)
	
	margin = fields.Float(
		string = "Margin %",
		defalut = 25.0,
		digits = "Product Price",
		help = "Margin over cost to calculate selling price"
		)
	
	markup = fields.Float(
		string = "Markup %",
		defalut = 33.33,
		digits = "Product Price",
		help = "Markup over cost to calculate selling price"
		)
	
	
	# === Radio button ==+ #
	
	@api.depends('price_type')
	def _get_price_type(self):
		for rec in self:
			selection = dict(rec._fields['price_type'].selection)
			rec.is_price_type = (selection.get(rec.price_type, '') == 'Margin')
	
	
	# === Onchange Logic === #
	
	@api.onchange('supplier_sales_price', 'supplier_discount')
	def _onchange_supplier_price_discount(self):
		for rec in self:
			if rec.supplier_sales_price:
				# Compute cost
				rec.standard_price = rec.supplier_sales_price * (1 - rec.supplier_discount / 100.0 or 0)
				# Recompute sale price
				rec._compute_sale_price()
	
	
	@api.onchange('standard_price')
	def _onchange_cost_price(self):
		for rec in self:
			if rec.supplier_sales_price:
				discount = 1 - (rec.standard_price / rec.supplier_sales_price)
				rec.supplier_discount = round(discount * 100, 2)
			rec._compute_sale_price()
	
	
	@api.onchange('price_type', 'margin', 'markup')
	def _onchange_pricing_strategy(self):
		self._compute_sale_price(True)
	
	
	@api.onchange('list_price')
	def _onchange_manual_sale_price(self):
		for rec in self:
			diff = rec.list_price - rec.standard_price
			
			if rec.is_price_type and rec.list_price:
				rec.margin = round((diff / rec.list_price) * 100, 2)
			
			if not rec.is_price_type and rec.standard_price:
				rec.markup = round(diff / rec.standard_price * 100, 2)
			
			
			result = {}
			if rec.is_price_type and rec.margin < 20:
				result['warning'] = {
					'title': " -- Warning Margin - - ",
					'message': f"MARGIN is below 25%, it is now: {rec.margin} %. change it if not intended",
					}
			if not rec.is_price_type and rec.markup < 20:
				result['warning'] = {
					'title': " -- Warning Markup - - ",
					'message': f"MARKUP is below 33.33%, it is now: {rec.markup} %. change it if not intended",
					}
			
			return result or None
		return None
	
	
	def _compute_sale_price(self, force_zero = False):
		for rec in self:
			
			if rec.is_price_type and (rec.margin != 0 or force_zero):
				rec.list_price = rec.standard_price / (1 - rec.margin / 100.0)
			
			elif not rec.is_price_type and (rec.markup != 0 or force_zero):
				rec.list_price = rec.standard_price * (1 + rec.markup / 100.0)
			
			elif rec.is_price_type and rec.margin == 0:
				rec._onchange_manual_sale_price()
			
			elif not rec.is_price_type and rec.markup == 0:
				rec._onchange_manual_sale_price()
