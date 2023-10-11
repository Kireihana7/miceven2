# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    _description = 'crm'


    invoiced_target_kl = fields.Integer(
        string='Meta de Facturación en Kg',
        help="Objetivo de ingresos para el mes actual en Kg")

    def update_invoiced_target(self, value):
        return self.write({'invoiced_target_kl': round(float(value or 0))})
		