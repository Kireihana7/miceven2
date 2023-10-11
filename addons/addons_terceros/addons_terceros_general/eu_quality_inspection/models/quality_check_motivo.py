# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class QualityCheckMotivo(models.Model):
    _name = "quality.check.motivo"
    _description = "Motivos para Calidad"


    quality_check = fields.Many2one('quality.check',string="Orden de Calidad")
    name = fields.Many2one('quality.check.motivo.detail',string="Motivo")
    quantity = fields.Char(string="Cantidad")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
