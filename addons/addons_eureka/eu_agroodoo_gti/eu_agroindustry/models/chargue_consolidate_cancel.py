# -*- coding: utf-8 -*-

from odoo import api,fields,models,_

class ChargueConsolidateCancel(models.Model):
    _name = "chargue.consolidate.cancel"
    _description = "Motivo de Cancelación Romana"

    name = fields.Char(string='Motivo de Cancelación')
