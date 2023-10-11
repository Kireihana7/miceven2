# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    apply_tolerance = fields.Boolean('Aplica Tolerencia', default = False)
    @api.onchange('bom_line_ids','bom_line_ids.product_principal_id','bom_line_ids.emp_primary','bom_line_ids.emp_secondary')
    def comprobar_activos_primary(self):
        for rec in self:
            if len(rec.bom_line_ids.filtered(lambda x: x.product_principal_id == True)) >1:
                raise UserError(_('No puede seleccionar mas de un producto principal'))
            if len(rec.bom_line_ids.filtered(lambda x: x.emp_primary == True)) >1:
                raise UserError(_('No puede seleccionar mas de un producto como empaque primario'))


