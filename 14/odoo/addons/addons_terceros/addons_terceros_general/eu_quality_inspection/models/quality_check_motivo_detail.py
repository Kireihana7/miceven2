# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class QualityCheckMotivoDetail(models.Model):
    _name = "quality.check.motivo.detail"
    _description = "Motivos para Calidad Detalle"

    name = fields.Char(string='Motivo')
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)