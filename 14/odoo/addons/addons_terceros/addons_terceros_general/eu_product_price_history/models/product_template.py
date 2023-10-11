
from datetime import datetime
from odoo import models, fields, api


class ProducTemplateHistoryPrice(models.Model):
    _inherit='product.template'
    
    
    history_price_ids = fields.One2many('product.price.history', 'product_tmpl_id')

    @api.constrains('standard_price')
    def check_create_history_price (self):
            for rec in self:
                if len(rec.attribute_line_ids) < 1:

                    self.env['product.price.history'].sudo().create({
                        'name' : rec.name,
                        'price_change_date' : datetime.today(),
                        'price_producto_standard' : rec.standard_price,
                        'precio_ref' : rec.standard_price * self.env.company.currency_id.rate,
                        'company_id': self.env.company.id,
                        'product_tmpl_id': rec.id,
                    })          


