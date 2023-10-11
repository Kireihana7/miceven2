# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = "stock.picking"

    def _get_overprocessed_stock_moves(self):
        self.ensure_one()
        return self.move_lines.filtered(
            lambda move: move.product_uom_qty != 0 and float_compare(move.quantity_done, move.product_uom_qty,
                                                                     precision_rounding=move.product_uom.rounding) == 1
        )

    def button_validate(self):
        if self._get_overprocessed_stock_moves():
            raise UserError('La cantidad Realizada no debe ser mayor a la cantidad Demandada')
        return  super(Picking, self).button_validate()
