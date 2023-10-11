from odoo import models, fields,api,_
from odoo.exceptions import UserError

class ProductSac(models.Model):
    _name = "product.saco"
    _description = 'Tipo de Saco'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",required=True)
    peso = fields.Float(string="Peso",required=True)
    precio = fields.Float(string="Precio Caleta",required=True)
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'peso'])
        return [(template.id, '%s - %s' % (template.name and 'Nombre: %s Peso: ' % template.name or '', template.peso or ''))
                for template in self]