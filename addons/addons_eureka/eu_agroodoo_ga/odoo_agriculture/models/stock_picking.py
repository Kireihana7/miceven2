# -*- coding: utf-8 -*-

from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        tracking=True
    ) 

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisición de Compra',
        readonly=True,
        copy=False,
        tracking=True
    )

    agriculture_cost_sheet_id = fields.Many2one('agriculture.cost.sheet', string='Workday Planning', required=False, tracking=True)    

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 0)],
        string='Finca',
        # required=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 1)],
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )           

class StockMove(models.Model):
    _inherit = 'stock.move'

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        tracking=True
    )     
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Línea de Requisición',
        copy=False,
        tracking=True
    )

    custom_cost_sheet_line_id = fields.Many2one(
        'agriculture.cost.sheet.lines',
        string='Job Cost Sheet Line',
        copy=False,
        tracking=True
    )    

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 0)],
        string='Finca',
        # required=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 1)],
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )       

    # crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=True, tracking=True)
    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
