# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class QualityCheckTabla(models.Model):
    _inherit = "quality.check.tabla"

    resultado = fields.Selection(
        [
            ('conforme','Conforme'),
            ('caracte','Característico'),
            ('no_conforme','No Conforme')
        ],
        string="Resultado Obtenido",
        default="conforme"
    )