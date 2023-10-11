# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    propiedades_promedio = fields.One2many('product.template.propiedades', 'product_id',string="Propiedades Vinculadas")

    def action_open_wizard(self):
        if not self.product_operation:
            raise UserError(_('Por favor, seleccione una Operación.'))
        if not self.quality_tabla:
            raise UserError(_('No hay datos en la Tabla de Propiedades'))
        return {
            'name': "Certificado de Calidad",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'quality.check.wizard',
            'view_id': self.env.ref('eu_quality_check_report.view_wizard_quality_check_form').id,
            'target': 'new',
        }






    