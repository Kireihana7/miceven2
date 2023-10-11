# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    extraction_flour = fields.Float(string='Porcentaje de Extracción', compute="_compute_extraction_flour", store=True )
    extraction_porcent = fields.Float(string='Margen de Tolerancia',compute="_compute_porcent")

    put_apply_tolerance = fields.Boolean(related='bom_id.apply_tolerance')

    @api.depends('qty_producing','move_raw_ids','move_raw_ids.quantity_done')
    def _compute_extraction_flour(self):
        for rec in self:
            rec.extraction_flour = 0
            principal = sum(rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True).mapped('quantity_done'))
            if principal > 0:
                rec.extraction_flour = (rec.qty_producing / principal)* 100

    @api.depends('qty_producing','move_raw_ids.quantity_done','move_byproduct_ids.quantity_done')
    def _compute_porcent(self):
        for rec in self:
            rec.extraction_porcent = 0
            principal = sum(rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True).mapped('quantity_done'))            
            tot_principal = rec.qty_producing
            sum_byproducts = sum(rec.move_byproduct_ids.filtered(lambda x: x.aprovechable == True).mapped('quantity_done'))
            resul = tot_principal + sum_byproducts
            if principal > 0:
                rec.extraction_porcent = (resul / principal) * 100

    # def write(self,vals):
    #     res = super(MrpProduction,self).write(vals)
    #     for rec in self:
    #         rec.actualizar_margen()
    #     return res

    # @api.model
    # def create(self,vals):
    #     res = super(MrpProduction,self).create(vals)
    #     for rec in res:
    #         if rec.put_apply_tolerance:
    #             rec.actualizar_margen()
    #     return res

    # def actualizar_margen(self):
    #     for rec in self:
    #         checkeo_duplicidad=rec.extraction_porcent
    #         principal = sum(rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True).mapped('quantity_done'))            
    #         sum_byproducts = sum(rec.move_byproduct_ids.filtered(lambda x: x.aprovechable == True).mapped('quantity_done'))
    #         resul = rec.qty_producing + sum_byproducts
    #         total = (resul / principal) * 100 if resul != 0 and principal != 0 else 0
    #         if principal > 0 and rec.extraction_porcent != total and checkeo_duplicidad !=(resul / principal) * 100:
    #             rec.extraction_porcent = (resul / principal) * 100

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for rec in self:
            principal = False
            if rec.put_apply_tolerance:
                # rec._compute_porcent()
                principal = rec.move_raw_ids.filtered(lambda x: x.product_principal_id == True)
                if principal:
                    if rec.extraction_porcent < 99.9:
                        raise UserError('No se puede procesar ya que el Margen de Tolerancia es menor al 99,9% \n * Por favor verificar cantidades de Productos Terminados y Sub-productos')
                    if rec.extraction_porcent > 100:
                        raise UserError('No se puede procesar ya que el Margen de Tolerancia supera el 100%')
        return res