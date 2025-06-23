from odoo import models, fields


class SalesOrder(models.Model):
	_name = 'custom.sales.order'
	_description = 'Sales Order'
	
	order_number = fields.Char(string = "Order Number")
	order_date = fields.Date(string = "Order Date")
	requested_delivery_date = fields.Date(string = "Requested Delivery Date")
	currency = fields.Char(string = "Currency")
	
	buyer_id = fields.Many2one('custom.partner', string = "Buyer", ondelete = 'cascade')
	seller_id = fields.Many2one('custom.partner', string = "Seller", ondelete = 'cascade')
	delivery_address_id = fields.Many2one('custom.address', string = "Delivery Address", ondelete = 'cascade')
	
	order_line_ids = fields.One2many('custom.sales.order.line', 'sales_order_id', string = "Order Lines")


class Partner(models.Model):
	_name = 'custom.partner'
	_description = 'Partner Details'
	
	gln = fields.Char(string = "GLN")
	name = fields.Char(string = "Name")
	address_id = fields.Many2one('custom.address', string = "Address", ondelete = 'cascade')
	contact_id = fields.Many2one('custom.contact', string = "Contact", ondelete = 'cascade')


class Address(models.Model):
	_name = 'custom.address'
	_description = 'Address Details'
	
	name = fields.Char(string = "Name")  # For Delivery Address Name or similar
	street = fields.Char(string = "Street")
	house_number = fields.Char(string = "House Number")
	postal_code = fields.Char(string = "Postal Code")
	city = fields.Char(string = "City")
	country_code = fields.Char(string = "Country Code")


class Contact(models.Model):
	_name = 'custom.contact'
	_description = 'Contact Details'
	
	name = fields.Char(string = "Name")
	phone = fields.Char(string = "Phone")
	email = fields.Char(string = "Email")


class SalesOrderLine(models.Model):
	_name = 'custom.sales.order.line'
	_description = 'Sales Order Line'
	
	sales_order_id = fields.Many2one('custom.sales.order', string = "Sales Order", ondelete = 'cascade')
	line_number = fields.Integer(string = "Line Number")
	
	supplier_article_number = fields.Char(string = "Supplier Article Number")
	ean = fields.Char(string = "EAN")
	description = fields.Char(string = "Product Description")
	manufacturer = fields.Char(string = "Manufacturer")
	
	quantity = fields.Float(string = "Quantity")
	unit = fields.Char(string = "Unit")
	net_price = fields.Float(string = "Net Price")
	discount = fields.Float(string = "Discount")
	delivery_date = fields.Date(string = "Delivery Date")

# <?xml version="1.0" encoding="UTF-8"?>
# <SalesOrder version="5.0" xmlns="http://www.ketenstandaard.nl/salesorder/v5">
#   <Header>
#     <OrderNumber>ORD20250617001</OrderNumber>
#     <OrderDate>2025-06-17</OrderDate>
#     <Buyer>
#       <GLN>8712345000012</GLN>
#       <Name>Installatiebedrijf De Jong</Name>
#       <Address>
#         <Street>Mainweg</Street>
#         <HouseNumber>123</HouseNumber>
#         <PostalCode>1234AB</PostalCode>
#         <City>Amsterdam</City>
#         <CountryCode>NL</CountryCode>
#       </Address>
#       <Contact>
#         <Name>Jan de Jong</Name>
#         <Phone>0201234567</Phone>
#         <Email>inkoop@dejong.nl</Email>
#       </Contact>
#     </Buyer>
#     <Seller>
#       <GLN>8712345999999</GLN>
#       <Name>Technische Groothandel BV</Name>
#     </Seller>
#     <DeliveryAddress>
#       <Name>Bouwplaats Project X</Name>
#       <Street>Bouwweg</Street>
#       <HouseNumber>5</HouseNumber>
#       <PostalCode>5678CD</PostalCode>
#       <City>Rotterdam</City>
#       <CountryCode>NL</CountryCode>
#     </DeliveryAddress>
#     <RequestedDeliveryDate>2025-06-20</RequestedDeliveryDate>
#     <Currency>EUR</Currency>
#   </Header>
#   <OrderLines>
#     <OrderLine>
#       <LineNumber>1</LineNumber>
#       <Product>
#         <SupplierArticleNumber>SW1001</SupplierArticleNumber>
#         <EAN>8712345000001</EAN>
#         <Description>Wandschakelaar IP44 wit</Description>
#         <Manufacturer>ABB</Manufacturer>
#       </Product>
#       <Quantity>10</Quantity>
#       <Unit>ST</Unit>
#       <NetPrice>12.50</NetPrice>
#       <Discount>0.00</Discount>
#       <DeliveryDate>2025-06-20</DeliveryDate>
#     </OrderLine>
#     <OrderLine>
#       <LineNumber>2</LineNumber>
#       <Product>
#         <SupplierArticleNumber>KVK2025</SupplierArticleNumber>
#         <EAN>8712345000025</EAN>
#         <Description>Kabeldoos Ø60 mm met wartel</Description>
#         <Manufacturer>Attema</Manufacturer>
#       </Product>
#       <Quantity>50</Quantity>
#       <Unit>ST</Unit>
#       <NetPrice>1.35</NetPrice>
#       <Discount>0.00</Discount>
#       <DeliveryDate>2025-06-20</DeliveryDate>
#     </OrderLine>
#   </OrderLines>
# </SalesOrder>
