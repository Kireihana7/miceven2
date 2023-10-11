# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_principal_id = fields.Boolean(string='Producto Principal',default=False, store=True, force_save=True,compute="_compute_productos")
    emp_primary = fields.Boolean(string='Empaque Primario', default=False, store=True,force_save=True, compute="_compute_productos")
    emp_secondary = fields.Boolean(string='Empaque Secundario', default=False, store=True,force_save=True, compute="_compute_productos")
    cinta_codificadora = fields.Boolean(string='Cinta Codificadora', default=False, store=True,force_save=True, compute="_compute_productos")
    teflon = fields.Boolean( string='Teflón',default=False, store=True, force_save=True, compute="_compute_productos")
    aprovechable = fields.Boolean( string='Aprovechable',default=False, store=True, force_save=True, compute="_compute_byproductos")

    @api.depends('bom_line_id')
    def _compute_productos(self):
        for rec in self:
            rec.product_principal_id = rec.bom_line_id.product_principal_id
            rec.emp_primary = rec.bom_line_id.emp_primary
            rec.emp_secondary = rec.bom_line_id.emp_secondary
            rec.cinta_codificadora = rec.bom_line_id.cinta_codificadora
            rec.teflon = rec.bom_line_id.teflon

    @api.depends('byproduct_id')
    def _compute_byproductos(self):
        for rec in self:
            rec.aprovechable = rec.byproduct_id.aprovechable
