from odoo import models, fields
from odoo import api

class Cart(models.Model):
    _name = 'mini_store.cart'
    _description = 'Shopping Cart'

    customer_id = fields.Many2one('mini_store.customer', string='Customer')
    cart_line_ids = fields.One2many('mini_store.cart_line', 'cart_id', string='Cart Lines')

class CartLine(models.Model):
    _name = 'mini_store.cart_line'
    _description = 'Cart Line'

    cart_id = fields.Many2one('mini_store.cart', string='Cart', required=True, ondelete='cascade')
    product_id = fields.Many2one('mini_store.product', string='Product', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    total_price = fields.Float(string='Total Price', compute='_compute_total_price')

    @api.depends('quantity', 'product_id.product_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.product_id.product_price