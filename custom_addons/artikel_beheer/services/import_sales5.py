def import_sales5(self, sales5_data):
    order_vals = {
        'order_id': sales5_data.get('order_id'),
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

    order_record = self.env['sales5.data'].create(order_vals)

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
