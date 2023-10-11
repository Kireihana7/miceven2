from odoo import api, models, modules,fields
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
class ProductTemplate(models.Model):
    _inherit="product.template"

class ProductProduct(models.Model):
    _inherit="product.product"



class StockMoveLine(models.Model):
    _inherit="stock.move.line"
        