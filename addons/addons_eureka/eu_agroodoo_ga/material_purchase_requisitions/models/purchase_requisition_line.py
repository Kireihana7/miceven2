# -*- coding: utf-8 -*-

from dataclasses import field
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"
    _description = 'Líneas de La Requisición'
    
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisiciones', tracking=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,tracking=True,
    ) 
    # product_brand_id = fields.Many2one(
    #     'pos.product.brand',
    #     related="product_id.product_brand_id",
    #     string="Marca",tracking=True,
    # )
    description = fields.Char(
        string='Descripción',
        required=True,tracking=True,
    )
    qty = fields.Float(
        string='Cantidad',
        default=1,
        required=True,tracking=True,
    )
    qty_available = fields.Float(
        string='Cantidad a mano',
        readonly=1,
        related="product_id.qty_available",tracking=True,
    )
    free_qty = fields.Float(
        string='Cantidad Disponible',
        readonly=1,
        related="product_id.free_qty",tracking=True,
    )
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True,tracking=True,)
    uom = fields.Many2one('uom.uom', string='Unidad de medida',tracking=True,)
    partner_id = fields.Many2many(
        'res.partner',
        string='Proveedor(es)',tracking=True,
    )
    requisition_type = fields.Selection(
        selection=[
                    ('internal','Requisición Interna'),
                    #('purchase','Requisición de Compra'),
                    ('tender','Licitación de Compra'),
        ],
        string='Tipo de Requisición',
        related='requisition_id.requisition_type',
        required=True,tracking=True,
    )
    product_category_id=fields.Many2one('product.category',related="product_id.categ_id", string="categoria de producto",tracking=True,)

    
    state = fields.Selection([ 
        ('0', 'Nuevas'), # 0 = draft
        ('1', 'Esperando Aprobación del Departamento'), # 1 = 1
        ('2', 'Esperando Aprobación del Gerente'), # 2 =2
        ('3', 'Aprobado'), # 3 = approve
        ('4', 'Requisición de Compra Creada'), # 4 = stock
        ('5', 'Recibidas'), # 5 = receive
        ('6', 'Canceladas'), # 6 = cancel
        ('7', 'Rechazadas')], # 7 = reject
        readonly=1,
        string='Estatus',
        related="requisition_id.state",
        store=True,tracking=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        required=False,
        compute="_compute_cost_center",
        string='Centro de Costo',
        store=True,
        readonly=False,
        copy=True,tracking=True,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsable de la requisición',
        copy=True,
        required=True,tracking=True,
        # domain="[('requisition_super', '=', True),('company_id', '=', company_id)]"
    )

    @api.depends('requisition_id','requisition_id.analytic_account_id')
    def _compute_cost_center(self):
        for rec in self:
            if not rec.analytic_account_id:
                rec.analytic_account_id=False
            if rec.requisition_id and rec.requisition_id.analytic_account_id:
                rec.analytic_account_id=rec.requisition_id.analytic_account_id

            
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
         #   rec.qty_available = rec.product_id.qty_available
