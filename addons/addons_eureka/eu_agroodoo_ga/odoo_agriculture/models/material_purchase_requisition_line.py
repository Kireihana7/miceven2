# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, RedirectWarning, UserError

class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        tracking=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        tracking=True
    )

    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
        string='Product Template ID',
        required=True,
        tracking=True
    )

    product_type = fields.Selection(
        related='product_tmpl_id.type',
        string='Type',
        required=True,
        tracking=True
    )   

    qty_available = fields.Float(
        string='Cantidad a mano',
        readonly=1,
        related="product_id.qty_available",
        tracking=True
    )

    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        string='Finca',
        # required=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        string='Tablón',
        required=False,
        tracking=True
    )        
    
    agriculture_company = fields.Boolean(related='requisition_id.agriculture_company')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
         #   rec.qty_available = rec.product_id.qty_available

    @api.onchange('qty')
    def onchange_qty(self):
        for rec in self:
            if rec.qty == 0:
                raise ValidationError(_('The quantity entered must be greater than 0.'))      