# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from itertools import groupby
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang, format_amount


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_line_agriculture = fields.One2many('purchase.order.line', 'order_id', string='Order Lines (Agriculture)', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    agriculture_company = fields.Boolean(related='company_id.agriculture_company')
    agricultural_purchase = fields.Boolean(string='Agricultural Purchase', default=True)
    agriculture_cost_sheet_id = fields.Many2one('agriculture.cost.sheet', string='Job Workday Planning')

    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name, 'default_picking_type_id': self.picking_type_id.id}
        pick_ids = self.mapped('picking_ids')
        
        for line in self.order_line:
            obj = self.env['stock.move'].search([('purchase_line_id', '=', line.id)])
            obj.update({
                # UPDATE:
                'farmer_request_id': line.farmer_request_id.id,
                
                'analytic_account_id_1': line.analytic_account_id_1.id,
                'analytic_account_id_2': line.analytic_account_id_2.id,
                'analytic_account_id_3': line.analytic_account_id_3.id,
                'analytic_account_id_4': line.analytic_account_id_4.id
            })

        '''
        index = 0
        for move in self.order_line.move_ids:
            # obj = 
            row = values[index]
            move.update({
                'analytic_account_id_1': row['analytic_account_id_1'],
                'analytic_account_id_2': row['analytic_account_id_2'],
                'analytic_account_id_3': row['analytic_account_id_3'],
                'analytic_account_id_4': row['analytic_account_id_4']                
            })
            index += 1           
        '''     
        

        # raise UserError(_(f'Pickings (1): {self.order_line.move_ids.purchase_line_id}'))
        # raise UserError(_(f'Pickings (1): {self.order_line.move_ids}'))


        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result
        

    '''
    def button_confirm(self):
        raise UserError(_('Test'))    
    '''

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_id = fields.Many2one('product.product', 
        string='Product',       
        tracking=True,
    )
    
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id",             
        tracking=True)

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        tracking=True
    )    

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 0)],
        string='Finca',
        # required=True,
        readonly=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 1)],
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        # domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )        
    
    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)    
    task_id = fields.Many2one('project.task', string='Task', required=False, tracking=True)
    custom_cost_sheet_line_id = fields.Many2one(
        'agriculture.cost.sheet.lines',
        string='Job Cost Sheet Line',
        copy=False,
        tracking=True
    )

    def _prepare_account_move_line(self):
        res = super()._prepare_account_move_line()      
        res.update({
            # UPDATE:
            'farmer_request_id': self.farmer_request_id.id,
            
            # UPDATE:
            'crop_request_transaction_id': self.crop_request_transaction_id.id,
            'crop_request_transaction_line_id': self.crop_request_transaction_line_id,
            'custom_cost_sheet_line_id': self.custom_cost_sheet_line_id.id,
            
            # UPDATE:
            'task_id': self.task_id.id,

            'analytic_account_id_1': self.analytic_account_id_1.id,
            'analytic_account_id_2': self.analytic_account_id_2.id,
            'analytic_account_id_3': self.analytic_account_id_3.id,
            'analytic_account_id_4': self.analytic_account_id_4.id,       
        })    
        return res