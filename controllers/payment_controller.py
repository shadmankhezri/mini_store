from odoo import http
from odoo.http import request
import requests

class PaymentController(http.Controller):

    @http.route('/payment/verify/<int:order_id>', type='http', auth='public', website=True)
    def verify_payment(self, order_id, **kw):
        order = request.env['mini_store.sale_order'].sudo().browse(order_id)
        authority = kw.get('Authority')
        status = kw.get('Status')

        if status == 'OK':
            # تایید نهایی پرداخت
            amount = int(order.total_price * 10)
            data = {
                'merchant_id': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
                'amount': amount,
                'authority': authority
            }
            res = requests.post('https://sandbox.zarinpal.com/pg/v4/payment/verify.json', json=data)
            result = res.json()

            if result['data']['code'] == 100:
                # موفقیت در پرداخت، تایید سفارش
                order.action_confirm_order()
                return request.render('mini_store.payment_success', {'order': order})
            else:
                return request.render('mini_store.payment_failed', {'error': 'پرداخت ناموفق بود.'})
        else:
            return request.render('mini_store.payment_failed', {'error': 'کاربر پرداخت را لغو کرد.'})
