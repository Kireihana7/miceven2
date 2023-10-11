# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    usar_patio_romana = fields.Boolean(
        "Usar patio", 
        config_parameter="eu_agroindustry.usar_patio_romana",
    )
    peso_liquidar_po = fields.Boolean(
        "Peso a liquidar en PO", 
        config_parameter="eu_agroindustry.peso_liquidar_po",
    )
    create_order_so = fields.Boolean(
        "Crear órden desde SO", 
        config_parameter="eu_agroindustry.create_order_so"
    )
    create_order_po = fields.Boolean(
        "Crear órden desde PO", 
        config_parameter="eu_agroindustry.create_order_po"
    )
    create_po_consolidate = fields.Boolean(
        "Crear PO desde ODD / ODC", 
        config_parameter="eu_agroindustry.create_po_consolidate"
    )
    confirm_po_consolidate = fields.Boolean(
        "Confirmar PO",
        config_parameter="eu_agroindustry.confirm_po_consolidate"
    )
    margen_tolerancia_romana = fields.Float(
        "Margen de tolerancia romana",
        config_parameter="eu_agroindustry.margen_tolerancia_romana"
    )
    descuento_permitido = fields.Float(
        "Cantidad de Descuento",
        config_parameter="eu_agroindustry.descuento_permitido"
    )