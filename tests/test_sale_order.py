from odoo.tests import TransactionCase
from odoo.exceptions import UserError

class TestSaleOrder(TransactionCase):
    def setUp(self):
        super().setUp()
       # Create test data
        self.customer = self.env['mini_store.customer'].create({
            'name': 'Test Customer',
            'national_id': '1234567890',
            'email': 'test@example.com',
            'phone': '09123456789',
        })
        self.product = self.env['mini_store.product'].create({
            'name': 'Test Product',
            'product_price': 100.0,
            'stock_quantity': 10,
        })
        self.sale_order = self.env['mini_store.sale_order'].create({
            'customer_id': self.customer.id,
            'order_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 2,
            })],
        })

    def test_compute_total_price(self):
        """Test calculating the total order price"""
        self.assertEqual(self.sale_order.total_price, 200.0, "Total price should be 2 * 100 = 200")

    def test_action_confirm_order(self):
        """Order Confirmation and Inventory Reduction Test"""
        initial_stock = self.product.stock_quantity
        self.sale_order.action_confirm_order()
        self.assertEqual(self.sale_order.state, 'confirmed', "Order state should be confirmed")
        self.assertEqual(self.product.stock_quantity, initial_stock - 2, "Stock should decrease by 2")
        # Invoice creation test
        invoice = self.env['mini_store.invoice'].search([('sale_order_id', '=', self.sale_order.id)])
        self.assertTrue(invoice, "Invoice should be created")
        self.assertEqual(invoice.state, 'paid', "Invoice should be paid")

    def test_insufficient_stock(self):
        """Error test for insufficient inventory"""
        self.sale_order.order_line_ids[0].quantity = 20  # More than stock
        with self.assertRaises(UserError):
            self.sale_order.action_confirm_order()