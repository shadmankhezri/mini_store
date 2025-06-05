from odoo import models, fields, api


class Product(models.Model):
    _name = "mini_store.product"
    _description = "Product"

    name = fields.Char(string="Product Name", required=True)
    product_price = fields.Float(string="Product Price", required=True)
    stock_quantity = fields.Integer(string="Stock Quantity", default=0)
    description = fields.Text(string="Description")

    
    category_id = fields.Many2one('mini_store.category', string="Category")

    image = fields.Image(string="Product Image")
    image_ids = fields.One2many('mini_store.product_image', 'product_id', string='Images')

    low_stock = fields.Boolean(string="Low Stock", compute="_compute_low_stock", store=True)

 
    @api.depends('stock_quantity')
    def _compute_low_stock(self):
        for product in self:
            product.low_stock = product.stock_quantity <= 5
            # if product.low_stock:
            #     self.env['mail.mail'].create({
            #         'subject': f'Low Stock Alert: {product.name}',
            #         'email_to': 'admin@example.com',
            #         'body_html': f'Product {product.name} has low stock: {product.stock_quantity}',
            #     }).send()

    
class ProductImage(models.Model):
    _name = 'mini_store.product_image'
    _description = 'Product Images'

    product_id = fields.Many2one('mini_store.product', string='Product', required=True, ondelete='cascade')
    image = fields.Image(string='Image')
