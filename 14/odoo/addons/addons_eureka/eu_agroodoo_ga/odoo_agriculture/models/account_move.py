# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    invoice_agriculture_line_ids = fields.One2many('account.move.line', 'move_id', string='Invoice lines (Agriculture)',
        copy=False, readonly=True,
        domain=[('exclude_from_invoice_tab', '=', False)],
        states={'draft': [('readonly', False)]})

    agriculture_company = fields.Boolean(related='company_id.agriculture_company')

    # def action_post(self):
    #     #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
    #     res = super(AccountMove, self).action_post()
    #     return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    agriculture_company = fields.Boolean(related='move_id.agriculture_company')

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
    custom_cost_sheet_line_id = fields.Many2one(
        'agriculture.cost.sheet.lines',
        string='Job Cost Sheet Line',
        tracking=True
    )            
    task_id = fields.Many2one('project.task', string='Task', required=False, tracking=True)

    def _prepare_analytic_line(self): 
        if self.agriculture_company == False:
            # Original:
            result = super(AccountMoveLine, self)._prepare_analytic_line()
            return result
        else:
            # Versión agrícola:
            """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
                an analytic account. This method is intended to be extended in other modules.
                :return list of values to create analytic.line
                :rtype list
            """
            result = []
            for move_line in self:
                amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
                default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
                
                finca_id = self.env['farmer.cropping.request'].search([('id', '=', move_line.farmer_request_id.id)]).finca_id.id
                # task_id = move_line.crop_request_transaction_id.task_id.id
                task_id = move_line.task_id.id
                parcel_id = self.env['farmer.cropping.request'].search([('id', '=', move_line.farmer_request_id.id)]).parcel_id.id
                tablon_id = self.env['farmer.cropping.request'].search([('id', '=', move_line.farmer_request_id.id)]).tablon_id.id
                
                result.append({
                    'name': default_name,
                    'date': move_line.date,
                    'account_id': move_line.analytic_account_id.id,

                    # UPDATE:
                    'farmer_request_id': move_line.farmer_request_id.id,

                    # UPDATE:
                    'finca_id': finca_id,
                    'task_id': task_id,
                    'parcel_id': parcel_id,
                    'tablon_id': tablon_id,

                    # UPDATE:
                    'crop_request_transaction_id': move_line.crop_request_transaction_id.id,
                    'crop_request_transaction_line_id': move_line.crop_request_transaction_line_id,
                    'custom_cost_sheet_line_id': move_line.custom_cost_sheet_line_id.id,

                    # New Fields:
                    'analytic_account_id_1': move_line.analytic_account_id_1.id,
                    'analytic_account_id_2': move_line.analytic_account_id_2.id,
                    'analytic_account_id_3': move_line.analytic_account_id_3.id,
                    'analytic_account_id_4': move_line.analytic_account_id_4.id,

                    'group_id': move_line.analytic_account_id.group_id.id,
                    'tag_ids': [(6, 0, move_line._get_analytic_tag_ids())],
                    'unit_amount': move_line.quantity,
                    'product_id': move_line.product_id and move_line.product_id.id or False,
                    'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
                    'amount': amount,
                    'general_account_id': move_line.account_id.id,
                    'ref': move_line.ref,
                    'move_id': move_line.id,
                    'user_id': move_line.move_id.invoice_user_id.id or self._uid,
                    'partner_id': move_line.partner_id.id,
                    'company_id': move_line.analytic_account_id.company_id.id or move_line.move_id.company_id.id,
                })
            return result

    # ============================================================ #
    def _prepare_analytic_distribution_line(self, distribution):
        if self.agriculture_company == False:
            # Original:
            result = super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution)
            return result
        else:        
            # Versión agrícola:
            """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
                analytic tags with analytic distribution.
            """
            self.ensure_one()
            amount = -self.balance * distribution.percentage / 100.0
            default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
            return {
                'name': default_name,
                'date': self.date,
                'account_id': distribution.account_id.id,

                # UPDATE:
                'farmer_request_id': distribution.farmer_request_id.id,

                # UPDATE:
                'crop_request_transaction_id': distribution.crop_request_transaction_id.id,
                'crop_request_transaction_line_id': distribution.crop_request_transaction_line_id,
                'custom_cost_sheet_line_id': distribution.custom_cost_sheet_line_id.id,

                # New Fields:
                'analytic_account_id_1': distribution.analytic_account_id_1.id,
                'analytic_account_id_2': distribution.analytic_account_id_2.id,
                'analytic_account_id_3': distribution.analytic_account_id_3.id,
                'analytic_account_id_4': distribution.analytic_account_id_4.id,

                'group_id': distribution.account_id.group_id.id,
                'partner_id': self.partner_id.id,
                'tag_ids': [(6, 0, [distribution.tag_id.id] + self._get_analytic_tag_ids())],
                'unit_amount': self.quantity,
                'product_id': self.product_id and self.product_id.id or False,
                'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
                'amount': amount,
                'general_account_id': self.account_id.id,
                'ref': self.ref,
                'move_id': self.id,
                'user_id': self.move_id.invoice_user_id.id or self._uid,
                'company_id': distribution.account_id.company_id.id or self.env.company.id,
            }        

    # ============================================================ #
    def create_analytic_lines(self):
        for rec in self:
            if rec.agriculture_company == False:
                # Original:
                super(AccountMoveLine, rec).create_analytic_lines()
            else:
                # Versión agrícola:
                """ Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
                """
                lines_to_create_analytic_entries = self.env['account.move.line']
                analytic_line_vals = []
                move_ids = []
                i = 0
                # for obj_line in self:
                for obj_line in rec:
                    move_ids.append(obj_line.move_id.id)
                    '''
                    for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
                        for distribution in tag.analytic_distribution_ids:
                            analytic_line_vals.append(obj_line._prepare_analytic_distribution_line(distribution))            
                    '''
                    if obj_line.analytic_account_id_1:
                        lines_to_create_analytic_entries += obj_line

                    if obj_line.analytic_account_id_2:
                        lines_to_create_analytic_entries += obj_line   

                    if obj_line.analytic_account_id_3:
                        lines_to_create_analytic_entries += obj_line   
                        
                    if obj_line.analytic_account_id_4:
                        lines_to_create_analytic_entries += obj_line  

                move_ids = list(dict.fromkeys(move_ids))   
                new_entries = self.env['account.move.line']

                i = 0
                for move_id in move_ids:
                    results = self.env['account.move.line'].search([('move_id', '=', move_id)])                                                               
                    j = 0
                    for record in results:
                        # Agregando línea analítica por cada Centro de Costo:
                        analytic_account = ''
                        if record.analytic_account_id_1:
                            record.analytic_account_id = record.analytic_account_id_1
                            # record.analytic_account_id = record.analytic_account_id_1
                            new_entries += record

                        if record.analytic_account_id_2:
                            record.analytic_account_id = record.analytic_account_id_2
                            # record.analytic_account_id = record.analytic_account_id_2
                            new_entries += record   

                        if record.analytic_account_id_3:
                            record.analytic_account_id = record.analytic_account_id_3
                            # record.analytic_account_id = record.analytic_account_id_3
                            new_entries += record   

                        if record.analytic_account_id_4:
                            record.analytic_account_id = record.analytic_account_id_4
                            # record.analytic_account_id = record.analytic_account_id_4
                            new_entries += record

                        '''
                        if j == 0:
                            analytic_account = record.analytic_account_id_1
                        elif j == 1:
                            analytic_account = record.analytic_account_id_2
                        elif j == 2:
                            analytic_account = record.analytic_account_id_3
                        else:
                            analytic_account = record.analytic_account_id_4                   
                        '''   
                        j += 1      
                                    
                    i += 1                

                # create analytic entries in batch
                '''
                if lines_to_create_analytic_entries:
                    analytic_line_vals += lines_to_create_analytic_entries._prepare_analytic_line()        
                '''

                if new_entries:
                    analytic_line_vals += new_entries._prepare_analytic_line()        
                
                # raise UserError(_(analytic_line_vals))

                i = 0
                move_id_list = []
                for record in analytic_line_vals:
                    row = analytic_line_vals[i]
                    move_id = analytic_line_vals[i]['move_id']
                    account_id = analytic_line_vals[i]['account_id']
                    move_id_list.append(move_id)
                    # print( f'{move_id} - {account_id}' )
                    i += 1

                # Registrando líneas analíticas:
                self.env['account.analytic.line'].create(analytic_line_vals)    

                # Eliminando duplicados:
                move_id_list = list(dict.fromkeys(move_id_list))   
                
                # Asignando (Modificando) el ID de cada Centro de Costo a cada línea analítica:
                for move_id in move_id_list:
                    index = 0
                    my_obj = self.env['account.analytic.line'].search([('move_id', '=', move_id)], order='id asc')
                    for record in my_obj:
                        id = record.id
                        account_id = ''
                        
                        field_jerarquia_analytic_account = ''
                        value_jerarquia_analytic_account = False 

                        if index == 0:
                            account_id = record.analytic_account_id_1.id

                            # UPDATE - Finca:
                            # field_jerarquia_analytic_account = 'finca_id'
                            # value_jerarquia_analytic_account = self.env['farmer.cropping.request'].search([('id', '=', record.farmer_request_id.id)]).finca_id.id                
                        elif index == 1:
                            account_id = record.analytic_account_id_2.id

                            # UPDATE - Tarea / Task:
                            # field_jerarquia_analytic_account = 'task_id'
                            # value_jerarquia_analytic_account = record.crop_request_transaction_id.task_id.id
                        elif index == 2:
                            account_id = record.analytic_account_id_3.id

                            # UPDATE - Parcela / Lote:
                            # Finca:
                            # if record.analytic_account_id_3:
                            #     field_jerarquia_analytic_account = 'parcel_id'
                            #     value_jerarquia_analytic_account = self.env['farmer.cropping.request'].search([('id', '=', record.farmer_request_id.id)]).parcel_id.id                       
                        else:
                            account_id = record.analytic_account_id_4.id                     

                            # UPDATE - Tablón:
                            # Finca:
                            # if record.analytic_account_id_4:
                            #     field_jerarquia_analytic_account = 'tablon_id'
                            #     value_jerarquia_analytic_account = self.env['farmer.cropping.request'].search([('id', '=', record.farmer_request_id.id)]).tablon_id.id                      
                        
                        num_parents = index
                        self.env['account.analytic.line'].search([('id', '=', id)]).write({
                            'account_id': account_id,
                            'num_parents': num_parents
                            # field_jerarquia_analytic_account: value_jerarquia_analytic_account
                        })              

                        index += 1            