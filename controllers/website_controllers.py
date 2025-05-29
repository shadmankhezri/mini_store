# mini_store/controllers/main.py
from odoo import http
from odoo.http import request

class ShopController(http.Controller):

#----------------------
# controller for product list
    @http.route('/shop/products', type='http', auth='public', website=True)
    def product_list(self, **kwargs):
        products = request.env['mini_store.product'].search([])
        return request.render('mini_store.product_list_template', {'products': products})
    
#----------------------
# controller for product detail
    @http.route('/shop/product/<int:product_id>', type='http', auth='public', website=True)
    def product_detail(self, product_id, **kwargs):
        product = request.env['mini_store.product'].browse(product_id)
        if not product.exists():
            return request.render('mini_store.payment_failed', {'error': 'Product not found'})
        return request.render('mini_store.product_detail_template', {'product': product})
    
#----------------------
# controller for submit_order
    @http.route('/shop/submit_order', type='http', auth='public', website=True, methods=['POST'])
    def submit_order(self, **post):
        customer_id = int(post.get('customer_id'))
        product_id = int(post.get('product_id'))
        quantity = int(post.get('quantity', 1))

        product = request.env['mini_store.product'].browse(product_id)
        if product.stock_quantity < quantity:
            return request.render('mini_store.payment_failed', {'error': 'There is not enough inventory'})

        order = request.env['mini_store.sale_order'].sudo().create({
            'customer_id': customer_id,
            'order_line_ids': [(0, 0, {
                'product_id': product_id,
                'quantity': quantity,
            })],
        })
        return request.redirect(f'/payment/verify/{order.id}')
    
#----------------------
# controller for invoice_detail
    @http.route('/shop/invoice/<int:invoice_id>', type='http', auth='public', website=True)
    def invoice_detail(self, invoice_id, **kwargs):
        invoice = request.env['mini_store.invoice'].browse(invoice_id)
        if not invoice.exists():
            return request.render('mini_store.payment_failed', {'error': 'Invoice not found'})
        return request.render('mini_store.invoice_template', {'invoice': invoice})
    
#----------------------
# controller for product_list_cached
    @http.route('/shop/products/cached', type='http', auth='public', website=True)
    def product_list_cached(self, **kwargs):
        products = request.env['mini_store.product'].search([])
        cache_key = f"product_list_{hash(str([p.write_date for p in products]))}"
        return request.render('mini_store.product_list_cached', {'products': products, 'cache_key': cache_key})
    
#----------------------
# controller for cart
    @http.route('/shop/cart', type='http', auth='public', website=True)
    def cart(self, **kwargs):
        cart = request.env['mini_store.cart'].sudo().search([('customer_id', '=', request.env.user.partner_id.id)], limit=1)
        if not cart:
            cart = request.env['mini_store.cart'].sudo().create({'customer_id': request.env.user.partner_id.id})
        return request.render('mini_store.cart_template', {'cart_items': cart.cart_line_ids})

# controller for add to cart
    @http.route('/shop/add_to_cart', type='http', auth='public', website=True, methods=['POST'])
    def add_to_cart(self, **post):
        product_id = int(post.get('product_id'))
        quantity = int(post.get('quantity', 1))
        cart = request.env['mini_store.cart'].sudo().search([('customer_id', '=', request.env.user.partner_id.id)], limit=1)
        if not cart:
            cart = request.env['mini_store.cart'].sudo().create({'customer_id': request.env.user.partner_id.id})

        cart.write({
            'cart_line_ids': [(0, 0, {
                'product_id': product_id,
                'quantity': quantity,
            })]
        })
        return request.redirect('/shop/cart')
    
#----------------------