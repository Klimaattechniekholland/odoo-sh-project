def import_or_update_sales5(self, sales5_data):
    """Create or update a Sales5 record based on order_id."""
    order_id = sales5_data.get('order_id')
    if not order_id:
        raise ValueError("Missing 'order_id' in Sales5 data.")

    sales_model = self.env['sales5.data']
    existing_order = sales_model.search([('order_id', '=', order_id)], limit=1)

    order_vals = {
        'order_date': sales5_data.get('order_date'),
        'customer_id': sales5_data.get('customer_id'),
        'customer_contact': sales5_data.get('customer_contact'),
        'customer_email': sales5_data.get('customer_email'),
        'shipping_street': sales5_data.get('shipping_address', {}).get('street'),
        'shipping_city': sales5_data.get('shipping_address', {}).get('city'),
        'shipping_postal_code': sales5_data.get('shipping_address', {}).get('postal_code'),
        'shipping_country': sales5_data.get('shipping_address', {}).get('country'),
        'total_before_tax': sales5_data.get('total_before_tax'),
        'tax_amount': sales5_data.get('tax_amount'),
        'total_amount': sales5_data.get('total_amount'),
        'currency': sales5_data.get('currency'),
        'payment_terms': sales5_data.get('payment_terms'),
        'expected_delivery_date': sales5_data.get('expected_delivery_date'),
        'status': sales5_data.get('status')
    }

    if existing_order:
        existing_order.write(order_vals)
        order_record = existing_order
    else:
        order_vals['order_id'] = order_id
        order_record = sales_model.create(order_vals)

    # Clean up old lines if updating
    order_record.line_ids.unlink()

    # Add new lines
    for line in sales5_data.get('order_lines', []):
        self.env['sales5.data.line'].create({
            'sales5_id': order_record.id,
            'line_number': line.get('line_number'),
            'product_id': line.get('product_id'),
            'description': line.get('description'),
            'quantity': line.get('quantity'),
            'unit_price': line.get('unit_price'),
            'discount_percent': line.get('discount_percent')
        })

    return order_record


def get_or_import_sales5(self, order_id):
    """Try fetching Sales5 externally, fallback to local creation if needed."""
    sales5_model = self.env['sales5.data']
    existing = sales5_model.search([('order_id', '=', order_id)], limit=1)

    if existing:
        _logger.info(f"[Sales5] Local record found for order {order_id}")
        return existing

    fetcher = Sales5Fetcher(self.env)
    sales5_data = fetcher.fetch_sales5(order_id)

    if sales5_data:
        _logger.info(f"[Sales5] Creating new Sales5 record from external data for order {order_id}")
        return sales5_model.import_or_update_sales5(sales5_data)

    _logger.warning(f"[Sales5] External fetch failed. Creating minimal placeholder for order {order_id}")
    return sales5_model.create({
        'order_id': order_id,
        'status': 'draft'
    })
