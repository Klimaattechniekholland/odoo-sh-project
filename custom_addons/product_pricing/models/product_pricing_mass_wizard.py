from itertools import islice

from odoo import api, fields, models
from odoo.exceptions import AccessError


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
	
	is_price_type_margin = fields.Boolean(
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
	
		
	def _chunked(self, records, size = 200):
		it = iter(records)
		while True:
			batch = tuple(islice(it, size))
			if not batch:
				return
			yield records.browse([record.id for record in batch])
	
	
	def action_apply_pricing(self):
		self.ensure_one()
		
		# Counters
		total = len(self.product_ids)
		cfg_writes = 0
		backfilled_supplier = 0
		cost_updates = 0
		price_updates = 0
		sudo_uses = 0
		errors = 0
		
		# Respect company context; don’t sudo unless needed
		products = self.product_ids.with_context(
			allowed_company_ids = self.env.context.get('allowed_company_ids') or [self.env.company.id]
			)
		
		# 1) One batch write for uniform config fields
		common_vals = {
			'price_type': self.price_type,
			'supplier_discount': self.supplier_discount,  # e.g. 25 for 25%
			}
		if self.is_price_type_margin:
			common_vals.update({'margin': self.margin, 'markup': 0.0})
		else:
			common_vals.update({'markup': self.markup, 'margin': 0.0})
		
		if common_vals:
			try:
				products.write(common_vals)
				cfg_writes = total
			except AccessError:
				products.sudo().write(common_vals)
				cfg_writes = total
				sudo_uses += 1
			except Exception:
				errors += 1  # generic catch; keep going
		
		# 2) Recompute prices in chunks
		for batch in self._chunked(products, size = 200):
			# 2a) Backfill supplier_sales_price if 0 and discount set
			to_backfill_supplier_price = []
			for item in batch:
				spp = item.supplier_sales_price or 0.0
				disc = (item.supplier_discount or 0.0) / 100.0
				if spp == 0.0 and 0.0 <= disc < 1.0 and (item.standard_price or 0.0) > 0.0:
					supplier_price = item.standard_price / (1.0 - disc)
					to_backfill_supplier_price.append((item, supplier_price))
			if to_backfill_supplier_price:
				try:
					for item, val in to_backfill_supplier_price:
						item.write({'supplier_sales_price': val})
						backfilled_supplier += 1
				except AccessError:
					for item, val in to_backfill_supplier_price:
						item.sudo().with_company(item.company_id).write({'supplier_sales_price': val})
						backfilled_supplier += 1
						sudo_uses += 1
				except Exception:
					errors += 1
			
			# 2b) Update COST (standard_price) from supplier price & discount
			to_cost = []
			for item in batch:
				if item.supplier_sales_price:
					disc = (item.supplier_discount or 0.0) / 100.0
					new_cost = item.supplier_sales_price * (1.0 - disc)
					if (item.standard_price or 0.0) != new_cost:
						to_cost.append((item, new_cost))
			if to_cost:
				try:
					for item, val in to_cost:
						item.write({'standard_price': val})
						cost_updates += 1
				except AccessError:
					for item, val in to_cost:
						item.sudo().with_company(item.company_id).write({'standard_price': val})
						cost_updates += 1
						sudo_uses += 1
				except Exception:
					errors += 1
			
			# 2c) Update LIST PRICE from margin/markup
			to_price = []
			for item in batch:
				cost = item.standard_price or 0.0
				if item.price_type == 'margin':
					m = (item.margin or 0.0) / 100.0
					if 0 < m < 1:
						price = cost / (1.0 - m)
						if (item.list_price or 0.0) != price:
							to_price.append((item, price))
				else:
					mu = (item.markup or 0.0) / 100.0
					price = cost * (1.0 + mu)
					if (item.list_price or 0.0) != price:
						to_price.append((item, price))
			if to_price:
				try:
					for item, val in to_price:
						item.write({'list_price': val})
						price_updates += 1
				except AccessError:
					for item, val in to_price:
						item.sudo().with_company(item.company_id).write({'list_price': val})
						price_updates += 1
						sudo_uses += 1
				except Exception:
					errors += 1
		
		# 3) Toast notification + close wizard
		msg_lines = [
			f"Selected: {total}",
			f"Config written: {cfg_writes}",
			f"Supplier price backfilled: {backfilled_supplier}",
			f"Cost updated: {cost_updates}",
			f"Sales price updated: {price_updates}",
			]
		if sudo_uses:
			msg_lines.append(f"Sudo fallbacks: {sudo_uses}")
		if errors:
			msg_lines.append(f"Errors: {errors} (check logs)")
		
		return {
			'type': 'ir.actions.client',
			'tag': 'display_notification',
			'params': {
				'title': "Mass Pricing Update",
				'message': "\n".join(msg_lines),
				'type': 'success' if not errors else 'warning',
				'sticky': False,
				'next': {'type': 'ir.actions.act_window_close'},
				},
			}
	
	
	# === Radio button === #
	
	@api.depends('price_type')
	def _get_price_type(self):
		for rec in self:
			selection = dict(rec._fields['price_type'].selection)
			rec.is_price_type_margin = (selection.get(rec.price_type, '') == 'Margin')
	
	
