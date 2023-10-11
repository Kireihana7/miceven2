# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.department'

    dest_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de Destino',
    )
    gerente = fields.Many2one('hr.employee',string="Gerente")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
