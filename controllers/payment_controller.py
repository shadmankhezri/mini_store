from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)

class PaymentController(http.Controller):

    @http.route('/payment/verify/<int:order_id>', type='http', auth='public', website=True)
    def verify_payment(self, order_id, **kw):
        try:
            order = request.env['mini_store.sale_order'].sudo().browse(order_id)
            if not order.exists():
                return request.render('mini_store.payment_failed', {
                    'error': 'سفارش یافت نشد.'
                })

            authority = kw.get('Authority')
            status = kw.get('Status')

            if status != 'OK':
                return request.render('mini_store.payment_failed', {
                    'error': 'کاربر پرداخت را لغو کرد.'
                })

            amount = int(order.total_price * 10)
            data = {
                'merchant_id': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
                'amount': amount,
                'authority': authority
            }

            try:
                response = requests.post(
                    'https://sandbox.zarinpal.com/pg/v4/payment/verify.json', 
                    json=data,
                    timeout=10  # اضافه شدن timeout برای جلوگیری از بی‌نهایت صبر کردن
                )
                result = response.json()
            except requests.exceptions.RequestException as req_err:
                _logger.exception("Zarinpal request failed")
                return request.render('mini_store.payment_failed', {
                    'error': 'اتصال به درگاه پرداخت با مشکل مواجه شد. لطفاً دوباره تلاش کنید.'
                })

            if result.get('data', {}).get('code') == 100:
                order.action_confirm_order()
                return request.render('mini_store.payment_success', {'order': order})
            else:
                error_msg = result.get('errors', {}).get('message', 'خطایی در تأیید پرداخت رخ داد.')
                _logger.error("Zarinpal error: %s", error_msg)
                return request.render('mini_store.payment_failed', {'error': error_msg})

        except Exception as e:
            _logger.exception("Unhandled payment verification error")
            return request.render('mini_store.payment_failed', {
                'error': 'مشکلی در فرآیند پرداخت به وجود آمد. لطفاً با پشتیبانی تماس بگیرید.'
            })
