# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tipo_kpi = fields.Selection([('branch','Sucursal'),('zona','Zona')],
        "Tipo KPI",
        config_parameter='eu_sales_kpi_kg_miceven.tipo_kpi'
    )