from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests

class SaleOrder(models.Model):
    _name = 'mini_store.sale_order'
    _description = 'Sale Order'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    customer_id = fields.Many2one('mini_store.customer', string='Customer', required=True)
    # product_id حذف شده چون اضافی به نظر می‌رسه
    order_date = fields.Datetime(string='Order Date', default=fields.Datetime.now)
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    # quantity حذف شده چون اضافی به نظر می‌رسه
    order_line_ids = fields.One2many('mini_store.sale_order_line', 'order_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    @api.depends('order_line_ids.total_price')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(line.total_price for line in order.order_line_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mini_store.sale_order') or 'New'
        return super(SaleOrder, self).create(vals)

    def action_pay_order(self):
        for order in self:
            for line in order.order_line_ids:
                if line.product_id.stock_quantity < line.quantity:
                    raise UserError(f"There is not enough inventory for product '{line.product_id.name}'")

            # ساخت callback_url با استفاده از web.base.url
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            callback_url = f'{base_url}/payment/verify/{order.id}'
            amount = int(order.total_price * 10)  # تبدیل به ریال

            # درخواست به درگاه پرداخت
            data = {
                'merchant_id': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',  # شناسه درگاه
                'amount': amount,
                'callback_url': callback_url,
                'description': f'پرداخت سفارش شماره {order.id}',
            }

            try:
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
                    error_message = result.get('errors', {}).get('message', 'Unknown error')
                    raise UserError(f"خطا در اتصال به درگاه پرداخت: {error_message}")
            except Exception as e:
                raise UserError(f"خطا در اتصال به درگاه: {str(e)}")

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
                
                # کاهش موجودی
                product.write({'stock_quantity': product.stock_quantity - line.quantity})
                line.invoice_id = invoice.id

            order.state = 'confirmed'

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

class SaleOrderLine(models.Model):
    _name = 'mini_store.sale_order_line'
    _description = 'Sale Order Line'

    order_id = fields.Many2one('mini_store.sale_order', string='Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('mini_store.product', string='Product', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    price_unit = fields.Float(string='Unit Price', related='product_id.product_price')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    invoice_id = fields.Many2one('mini_store.invoice', string='Invoice')

    @api.depends('quantity', 'price_unit')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.price_unit

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")



