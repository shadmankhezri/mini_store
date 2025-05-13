from odoo import models, fields,api
from odoo.exceptions import ValidationError
import re

class Customer(models.Model):
    _name = 'mini_store.customer'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Customer'
    
 

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')

    date_joined = fields.Datetime(string='Date Joined', default=fields.Datetime.now)
    sale_order_ids = fields.One2many('mini_store.sale_order', 'customer_id', string='Sale Orders history')
    total_spent = fields.Float(string='Total Spent', compute='_compute_total_spent')


    national_id = fields.Char(string='National ID', required=True)
    _sql_constraints = [
        ('unique_national_id', 'UNIQUE(national_id)', 'National ID must be unique.'),
    ]


#-----------------------------

    @api.constrains('national_id', 'phone', 'email')
    def _check_customer_fields(self):
        for record in self:
            # validation ID
            if not re.fullmatch(r'\d{10}', record.national_id or ''):
                raise ValidationError("National ID must be exactly 10 digits.")
            
            # validation phone number start with 0 and include 11 digits
            if record.phone and not re.fullmatch(r'0\d{10}', record.phone):
                raise ValidationError("Phone number must be 11 digits and start with 0.")
            
            # validation email
            if record.email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Invalid email format.")
    
#-----------------------------

    def _compute_total_spent(self):
        for record in self:
            total = sum(order.total_price for order in record.sale_order_ids)
            record.total_spent = total

