
from odoo import models, fields, api
from odoo.exceptions import UserError

import requests
from odoo.http import request
from odoo import http



class SaleOrder(models.Model):
    _name = 'mini_store.sale_order'
    _description = 'Sale Order'

    customer_id = fields.Many2one('mini_store.customer', string='Customer', required=True)
    product_id = fields.Many2one('product.product', string="Product")

    order_date = fields.Datetime(string='Order Date', default=fields.Datetime.now)

    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    quantity = fields.Integer('Quantity')

    order_line_ids = fields.One2many('mini_store.sale_order_line', 'order_id', string='Order Lines')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    @api.depends('order_line_ids.total_price')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(line.total_price for line in order.order_line_ids)

# ----------------------------


    @api.model_create_multi
    def create(self, vals_list):
        return super(SaleOrder, self).create(vals_list)

    


    def action_pay_order(self):
        for order in self:
            if order.total_price <= 0:
                raise UserError("مبلغ سفارش معتبر نیست.")

            # payment info
            callback_url = f'/payment/verify/{order.id}'
            amount = int(order.total_price * 10)  

            # request
            data = {
                'merchant_id': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',  # شناسه درگاه 
                'amount': amount,
                'callback_url': request.httprequest.host_url.rstrip('/') + callback_url,
                'description': f'پرداخت سفارش شماره {order.id}',
            }

            res = requests.post('https://sandbox.zarinpal.com/pg/v4/payment/request.json', json=data)
            result = res.json()

            if result['data']['code'] == 100:
                authority = result['data']['authority']
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'https://sandbox.zarinpal.com/pg/StartPay/{authority}',
                    'target': 'self',
                }
            else:
                raise UserError("خطا در اتصال به درگاه پرداخت.")


# ----------------------------

    def action_confirm_order(self):
        for order in self:
            if order.state == 'confirmed':
                raise UserError("This order is already confirmed.")

            invoice = self.env['mini_store.invoice'].create({
                'sale_order_id': order.id,
                'state': 'paid',
            })

            for line in order.order_line_ids:
                product = line.product_id
                if product.stock_quantity < line.quantity:
                    raise UserError(f"موجودی محصول '{product.name}' کافی نیست.")
            
                # decreas quantity
                product.write({'stock_quantity': product.stock_quantity - line.quantity})

            


                line.invoice_id = invoice.id

            order.state = 'confirmed'


# --------------------------------

    def action_fake_payment(self):
        for order in self:
            if order.state == 'confirmed':
                raise UserError("این سفارش قبلاً تایید شده است.")
        

            order.action_confirm_order()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'پرداخت با موفقیت انجام شد',
                'message': 'سفارش شما تایید شد و پرداخت تستی با موفقیت انجام شد.',
                'type': 'success',
                'sticky': True, 
            }
        }
