from odoo import models, fields

class Category(models.Model):
    _name = "mini_store.category"
    _description = "Product Category"
    _rec_name = "cat_name"

    cat_name = fields.Char(string="Category Name", required=True)
    description = fields.Text(string="Description")
    product_ids = fields.One2many('mini_store.product', 'category_id', string="Products")
    image = fields.Image(string="Category Image") 


    def name_get(self):
        result = []
        for record in self:
            name = record.cat_name or "Unnamed Category"
            result.append((record.id, name))
        return result