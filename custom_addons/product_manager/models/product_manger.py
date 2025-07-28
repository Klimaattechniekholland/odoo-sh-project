from odoo import api, fields, models


class ProductManager(models.Model):
	_name = 'product.manager'
	_description = 'Product Manager'
	
	# _inherit = ['product.template']
	
	_in_onchange = False  # Guard-flag for loops in onchange calls
	
	# type_product = fields.Char('Type')
	# brand_product = fields.Char('Brand')
	# product_code = fields.Char('Product Code')
	# product_short_name = fields.Char('Product Short Name')
	# product_ean_code = fields.Char('Product EAN Code')



	
	# Link to a specific product variant
	product_manager_id = fields.Many2one('product.product', string = "Product", required = True)

	#
	# sales price => product_id.list_price
	# cost price => product_id.standard_price
	#

	
	product_supplier_sales_price = fields.Float(
		string = "Supplier sales Price",
		digits = "Product Price",
		help = "Price of the supplier - manufacturer without our discount, "
		)
	
	
	product_supplier_discount = fields.Float(
		string = "Discount %",
		digits = "Product Price",
		help = "Buying Price of the supplier - manufacturer "
		)
	
	product_margin = fields.Float(
		string = "Margin %",
		digits = "Product Price",
		help = "Margin % we want to earn "
		)
	
	product_markup = fields.Float(
		string = "markup %",
		digits = "Product Price",
		help = "Markup % owe want, (not the price list value) "
		)
	
	product_use_margin = fields.Boolean(
		string = "use Margin",
		help = "Use Margin or Markup ",
		default = True
		)
	
	
	#
	# Calculate the cost price with our discount
	# Cost = Sales price  * (1 - Discount)
	# the cost price is also calculated with some price list on the supplier or with extra discounts
	# we need to refactor probably this , todo
	#
	
	def _compute_discount(self):
		for record in self:
			if record.product_supplier_sales_price > 0:
				discount = 1 - (self.product_manager_id.standard_price / self.product_supplier_sales_price)
				record.product_supplier_discount = round(discount, 2)
	
	
	
	def _compute_cost_price(self):
		for record in self:
			record.product_manager_id.standard_price = self.product_supplier_sales_price * (1 - self.product_supplier_discount)
	
	
	# we don't recalculate the product supplier sales price, that is normally fixed, just to be complete
	def _compute_supplier_sales_price(self):
		for record in self:
			if record.product_supplier_discount > 0:
				record.product_supplier_sales_price = self.product_manager_id.standard_price / (1 - self.product_supplier_discount)

	
	#
	# we normally calculate with margins not with markup's
	# markups are used in the odoo's price list!!! not very handy
	# Margin = (SellingPrice - Cost) / SellingPrice
	# Markup = (Selling Price - Cost) / Cost
	# for the same amount of money, the markup is always higher
	# Margin 25%, Markup 33,333% gives the same earnings
	#
	# sales price => list_price
	# cost price => standard_price
	#
	
	
	def _compute_sales_price(self):
		for record in self:
			if self.product_use_margin:
				if 0 < self.product_margin < 1:
					record.product_manager_id.list_price = record.product_manager_id.standard_price / (1 - self.product_margin)
			else:
				if 0 < self.product_markup < 1:
					record.product_manager_id.list_price = record.product_manager_id.standard_price * (1 * self.product_markup)


	def _compute_percentage(self):
		for record in self:
			amount = (record.product_manager_id.list_price - record.product_manager_id.standard_price)
			if amount > 0 :
				if self.product_use_margin:
					if record.product_manager_id.list_price > 0:
						record.product_margin = amount / record.product_manager_id.list_price
				else:
					if record.product_manager_id.standard_price > 0:
						record.product_markup = amount / record.product_manager_id.standard_price
			
				
	def _compute_costqqq_price(self):
		for record in self:
			if self.product_supplier_sales_price:
				record.product_manager_id.standard_price = record.product_manager_id.list_price / (1 - self.product_margin)
			else:
				record.product_manager_id.standard_price = record.product_manager_id.list_price * (1 * self.product_markup)


	# === Onchange ===#
	
	# top-down
	# change product_supplier_sale_price or product_supplier_discount ==>
	#     change the Cost (standard_price)
	#     change the Sale price (list_price)
	@api.depends('product_supplier_sales_price', 'product_supplier_discount')
	def _onchange_supplier_price_discount(self):
		if self._in_onchange:
			return
		try:
			self._in_onchange = True
			self._compute_cost_price()
			self._compute_sales_price()
		finally:
			self._in_onchange = False


	# change Cost (standard_price) ==>
	#     change the product_supplier_discount
	#     change the Sale price (list_price)
	@api.depends('product_manager_id.standard_price')
	def _onchange_cost_price(self):
		if self._in_onchange:
			return
		try:
			self._in_onchange = True
			self._compute_discount()
			self._compute_sales_price()
		finally:
			self._in_onchange = False
	
	
	# change product_use_margin or product_margin or product_markup==>
	#     change the Sale price (list_price)
	@api.depends('product_markup', 'product_margin', 'product_use_margin')
	def _onchange_product_percentage(self):
		if self._in_onchange:
			return
		try:
			self._in_onchange = True
			self._compute_sales_price()
		finally:
			self._in_onchange = False
		
		
	# change Sale price (list_price) ==>
	#     change the product_supplier_discount
	@api.depends('product_manager_id.list_price')
	def _onchange_sales_price(self):
		if self._in_onchange:
			return
		try:
			self._in_onchange = True
			self._compute_percentage()
		finally:
			self._in_onchange = False

























