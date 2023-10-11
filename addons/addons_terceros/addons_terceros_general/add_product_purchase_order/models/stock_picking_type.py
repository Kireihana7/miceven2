from odoo import models, fields,api,_
from odoo.exceptions import UserError

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    puesto_compra = fields.Boolean(string="Puesto de Compra")

    @api.onchange("puesto_compra")
    def _onchange_puesto_compra(self):
        for rec in self:
            if rec.puesto_compra:
                rec.use_existing_lots = True
                rec.use_create_lots = False
            else:
                rec.use_existing_lots = False
                rec.use_create_lots = True