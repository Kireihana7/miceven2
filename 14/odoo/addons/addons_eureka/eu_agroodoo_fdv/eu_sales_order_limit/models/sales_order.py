# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class SalesOder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_order_line_count(self):
        limit = self.env['res.company'].search([('id', '=', self.env.company.id)]).sale_order_limit
        for rec in self:
            total = len(rec.order_line)
            #SI ES IGUAL A 0 QUIERE DECIR QUE NO ESTA ESTABLECIDO
            if limit > 0 and total > limit:
                raise UserError(('El Limite Establecido de Productos a Facturar es de %s')%(limit))
