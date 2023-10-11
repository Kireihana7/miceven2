# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class QualityCheckMotivo(models.Model):
    _inherit = "quality.check.motivo"

    destino = fields.Selection(
        [
            ('Venta Industrial', 'Venta Industrial'),
            ('Reproceso', 'Reproceso'),
            ('Subproducto', 'Subproducto'),
            ('Desperdicio', 'Desperdicio')
        ],
        string="Destino"
    )