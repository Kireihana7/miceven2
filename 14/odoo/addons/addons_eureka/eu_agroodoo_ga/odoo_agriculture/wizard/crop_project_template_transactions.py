# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CropProjectTemplateTransactions(models.TransientModel):
    _name = "crop.project.template.transactions"
    
    @api.model
    def default_get(self, fields):
        res = super(CropProjectTemplateTransactions, self).default_get(fields)
        res['crop_project_template_id'] = self.env.context.get('default_crop_project_template_id')
        res['task_id'] = self.env.context.get('default_task_id')
        return res    

    crop_project_template_id = fields.Many2one('project.project', string='Project', readonly=True, tracking=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True, tracking=True)
    crop_request_transaction_ids = fields.Many2many(
        'crop.request.transaction', 
        relation='crop_project_template_wizard_transaction_rel', 
        # compute='_compute_reservation_ids', 
        string='Transactions associated to this Crop Project Template',
        # domain=[('crop_project_template_id', 'in', lambda self: self.crop_project_template_id.id)] 
        # store=True
        tracking=True
    )    

    
    @api.onchange('crop_request_transaction_ids')
    def _onchange_crop_request_transaction_ids(self):
        list_number_task_transactions = []
        task_transactions = self.env['crop.request.transaction'].search([
            ('crop_project_template_id', '=', self.crop_project_template_id.id),
            ('task_id', '=', self.task_id.id),
        ])

        for line in task_transactions:
            transaction_obj = self.env['crop.request.transaction'].search([('id', '=', line.id)])
            type = transaction_obj.type

            transacion_model = ''
            transacion_model_id = ''
            transacion_model_field_name = ''

            if type == 'equipment_reservation':                
                equipment_reservation_id = transaction_obj.equipment_reservation_id.id
                transacion_model = 'equipment.reservation'
                transacion_model_id = equipment_reservation_id
                transacion_model_field_name = 'equipment_reservation_id'  
            if type == 'labour_management':
                labour_management_id = transaction_obj.labour_management_id.id
                transacion_model = 'labour.management'
                transacion_model_id = labour_management_id
                transacion_model_field_name = 'labour_management_id'   
            if type == 'crop_material_management':
                crop_material_id = transaction_obj.crop_material_id.id
                transacion_model = 'crop.material.management'
                transacion_model_id = crop_material_id
                transacion_model_field_name = 'crop_material_id'

            number = self.env[transacion_model].search([('id', '=', transacion_model_id)]).number
            list_number_task_transactions.append(number)
        
        # ============================================================================ #
        # ============================================================================ #
        
        list_crop_request_transaction_ids = []
        obj = self.env['crop.request.transaction'].search([
            ('crop_project_template_id', '=', self.crop_project_template_id.id),
            ('task_id', '=', False),
        ])

        for line in obj:
            transaction_obj = self.env['crop.request.transaction'].search([('id', '=', line.id)])
            type = transaction_obj.type

            transacion_model = ''
            transacion_model_id = ''
            transacion_model_field_name = ''

            if type == 'equipment_reservation':                
                equipment_reservation_id = transaction_obj.equipment_reservation_id.id
                transacion_model = 'equipment.reservation'
                transacion_model_id = equipment_reservation_id
                transacion_model_field_name = 'equipment_reservation_id'  
            if type == 'labour_management':
                labour_management_id = transaction_obj.labour_management_id.id
                transacion_model = 'labour.management'
                transacion_model_id = labour_management_id
                transacion_model_field_name = 'labour_management_id'   
            if type == 'crop_material_management':
                crop_material_id = transaction_obj.crop_material_id.id
                transacion_model = 'crop.material.management'
                transacion_model_id = crop_material_id
                transacion_model_field_name = 'crop_material_id'

            number = self.env[transacion_model].search([('id', '=', transacion_model_id)]).number
            if number not in list_number_task_transactions:
                list_crop_request_transaction_ids.append(line.id)

        return {
            'domain': { 
                'crop_request_transaction_ids': [
                        ('crop_project_template_id', '=', self.crop_project_template_id.id), 
                        ('id', 'in', list_crop_request_transaction_ids),
                    ]
                }
        }    
    

    def action_add_transactions(self):
        task_id = self.env.context.get('default_task_id')
        # raise UserError(_(f'Task ID: {task_id}'))

        transaction_ids = self.crop_request_transaction_ids
        list_ids = []
        for transaction in transaction_ids:
            list_ids.append(transaction.id)

        # for id in list_ids:
        for id in list_ids: 
            my_id = self.env['crop.request.transaction'].browse(id).id
            transaction_obj = self.env['crop.request.transaction'].search([('id', '=', my_id)])
            type = transaction_obj.type

            transacion_model = ''
            transacion_model_id = ''
            transacion_model_field_name = ''

            if type == 'equipment_reservation':                
                equipment_reservation_id = transaction_obj.equipment_reservation_id.id
                transacion_model = 'equipment.reservation'
                transacion_model_id = equipment_reservation_id
                transacion_model_field_name = 'equipment_reservation_id'  
            if type == 'labour_management':
                labour_management_id = transaction_obj.labour_management_id.id
                transacion_model = 'labour.management'
                transacion_model_id = labour_management_id
                transacion_model_field_name = 'labour_management_id'   
            if type == 'crop_material_management':
                crop_material_id = transaction_obj.crop_material_id.id
                transacion_model = 'crop.material.management'
                transacion_model_id = crop_material_id
                transacion_model_field_name = 'crop_material_id'  

            self.env[transacion_model].search([('id', '=', transacion_model_id)]).copy({
                'task_id': task_id,
            })            
            
            '''
            self.env['crop.request.transaction'].search([(transacion_model_field_name, '=', transacion_model_id), ('task_id', '=', False)]).write({
                'task_ids': [
                    (0, 0, { task_id })
                ]
            })            
            '''
            
            self.env['crop.request.transaction'].search([])[-1].write({
                'state': 'added_from_cpt',
                'task_ids': [
                    (4, task_id, 0)
                ]                
            })                  
                    