# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self,vals):
        res  = super(StockPicking, self).write(vals)
        for rec in self:
            if rec.location_id == rec.location_dest_id:
                raise UserError('La Ubicación de Origen debe ser distinta a la ubicación de Destino')
            for line in rec.move_line_ids_without_package:
                if line.location_id == line.location_dest_id:
                    raise UserError('La Ubicación de Origen debe ser distinta a la ubicación de Destino')
            for lines in rec.move_ids_without_package:
                if lines.location_id == lines.location_dest_id:
                    raise UserError('La Ubicación de Origen debe ser distinta a la ubicación de Destino')
        return res


    #def button_validate(self):
    #    if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
    #        raise UserError(_('No puedes procesar más cantidades que la demanda inicial'))
    #    return super(StockPicking, self).button_validate()