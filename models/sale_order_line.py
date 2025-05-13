from odoo import models, fields, api




class SaleOrderLine(models.Model):
    _name = 'mini_store.sale_order_line'
    _description = 'Sale Order Line'

    order_id = fields.Many2one('mini_store.sale_order', string='Sale Order', required=True, ondelete='cascade')



    product_id = fields.Many2one('mini_store.product', string='Product', required=True)
    quantity = fields.Integer(string='Quantity', default=1)


    price_unit = fields.Float(string='Unit Price', related='product_id.product_price', store=True)
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)

    invoice_id = fields.Many2one('mini_store.invoice', string='Invoice')


    @api.depends('quantity', 'price_unit')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.price_unit
