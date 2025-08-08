from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductPricingMassWizard(models.TransientModel):
	_name = 'product.pricing.mass.wizard'
	_description = 'Mass Pricing Update for Product Templates'
	
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
	
	margin = fields.Float(string = "Margin %")
	markup = fields.Float(string = "Markup %")
	supplier_discount = fields.Float(string = "Supplier Discount %")
	
	category_id = fields.Many2one('product.category', string = "Filter by Category")
	
	supplier_id = fields.Many2one(
		'res.partner',
		string = 'Vendor',
		domain = [('supplier_rank', '>', 0)],
		help = 'Only apply to products supplied by this vendor'
		)
	
	product_ids = fields.Many2many(
		'product.template', string = "Products",
		default = lambda self: self.env.context.get('default_product_ids')
		)
	
	@api.onchange('category_id', 'supplier_id')
	def _onchange_filters(self):
		domain = []
		if self.category_id:
			domain.append(('categ_id', '=', self.product_category_id.id))
		if self.vendor_id:
			domain.append(('seller_ids.name', '=', self.vendor_id.id))
		if domain:
			products = self.env['product.template'].search(domain)
		else:
			products = self.env['product.template'].search([])
		
		self.product_ids = [(6, 0, products.ids)]
		
	
	def action_apply_pricing(self):
		for product in self.product_ids:
			product.price_type = self.price_type
			
			product.product_supplier_discount = self.supplier_discount
			if self.is_price_type:
				product.product_margin = self.margin
			else:
				product.product_markup = self.markup
			
			# Optional: recompute synced fields
			product._compute_cost_price()
			product._compute_sales_price()
	
	
	def apply_mass_pricing(self):
		if not self.product_ids:
			raise UserError(_("Please select at least one product."))
		
		# if not (0 < self.percentage < 100):
		# 	raise UserError(_("Percentage must be between 0 and 100."))
		
		pricing_model = self.env['product.template']
		
		for product in self.product_ids:
			# Auto-create pricing record if missing
			pricing = pricing_model.search([('id', '=', product.id)], limit = 1)
			if not pricing:
				pricing = pricing_model.create({'id': product.id})
			
			if self.price_type == 'margin':
				pricing.write(
					{
						'margin': self.percentage,
						'is_price_type': True,
						}
					)
			else:
				pricing.write(
					{
						'markup': self.percentage,
						'is_price_type': False,
						}
					)
			
			pricing._compute_sales_price()
	
	# === Radio button === #
	
	@api.depends('price_type')
	def _get_price_type(self):
		for rec in self:
			selection = dict(rec._fields['price_type'].selection)
			rec.is_price_type = (selection.get(rec.price_type, '') == 'Margin')


	def open_mass_pricing_wizard(self):
		return {
			'name': 'Mass Pricing Update',
			'type': 'ir.actions.act_window',
			'res_model': 'product.pricing.mass.wizard',
			'view_mode': 'form',
			'target': 'new',
			'context': {
				'default_product_ids': self.ids
				}
			}