# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
class Maintenance_correlative(models.Model) :
    _inherit = 'maintenance.request'

    correlative_name = fields.Char("Secuencia")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            rec.correlative_name = self.env['ir.sequence'].next_by_code(rec.company_id.maintenance_sequence.code)
        return res



