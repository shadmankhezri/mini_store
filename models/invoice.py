from odoo import models, fields, api
from odoo.exceptions import UserError

class Invoice(models.Model):
    _name = 'mini_store.invoice'
    _description = 'Invoice'

    name = fields.Char(string='Invoice Number', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('mini_store.invoice'))
    
    sale_order_id = fields.Many2one('mini_store.sale_order', string='Sale Order', required=True)
    customer_id = fields.Many2one(related='sale_order_id.customer_id', string='Customer', store=True)
    order_date = fields.Datetime(related='sale_order_id.order_date', string='Order Date', store=True)
    total_price = fields.Float(related='sale_order_id.total_price', string='Total Price', store=True)



    order_line_ids = fields.One2many('mini_store.sale_order_line', 'invoice_id', string='Order Lines')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid')
    ], string='Status', default='draft', tracking=True)

    def action_mark_as_paid(self):
        for invoice in self:
            if invoice.state == 'paid':
                raise UserError("This invoice is already paid.")
            invoice.state = 'paid'

