# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_principal_id = fields.Boolean(string='Producto Principal', default=False)
    emp_primary = fields.Boolean(string='Empaque Primario', default=False)
    emp_secondary = fields.Boolean(string='Empaque Secundario', default=False)
    cinta_codificadora = fields.Boolean(string='Cinta Codificadora', default=False)
    teflon = fields.Boolean(string='Teflón', default=False)

    @api.onchange('emp_primary')
    def comprobar_activos_emp_primary(self):
        for rec in self:
            if rec.product_principal_id == True:
                rec.emp_primary = False
                raise UserError('No puede seleccionar ya que se encuentra como producto principal')

            if rec.emp_secondary == True:
                rec.emp_primary = False
                raise UserError('No puede seleccionar ya que esta asignado como producto de empaque secundario')

    @api.onchange('emp_secondary')
    def comprobar_activos_emp_secondary(self):
        for rec in self:
            if rec.product_principal_id == True:
                rec.emp_secondary = False
                raise UserError('No puede seleccionar ya que se encuentra como producto principal')

            if rec.emp_primary == True:
                rec.emp_secondary = False
                raise UserError('No puede seleccionar ya que esta asignado como producto de empaque primario')

    @api.onchange('product_principal_id')
    def comprobar_activos_product_principal_id(self):
        for rec in self:
            if rec.emp_primary == True or rec.emp_secondary == True:
                rec.product_principal_id = False
                raise UserError('No puede seleccionar ya que esta asignado como producto de empaque primario o producto de empaque secundario')