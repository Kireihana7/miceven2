# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CropRequestRecordsRequisitionWizard(models.TransientModel):
    _name = "crop.request.records.requisition.wizard"
    
    @api.model
    def default_get(self, fields):
        res = super(CropRequestRecordsRequisitionWizard, self).default_get(fields)
        res['farmer_request_id'] = self.env.context.get('default_farmer_request_id')
        res['project_id'] = self.env.context.get('default_project_id')
        res['usar_tareas'] = self.env.context.get('default_usar_tareas')
        return res    
    
    usar_tareas = fields.Boolean(
        string='Use Activities Template',
        required=True,
        tracking=True
    )    
    farmer_request_id = fields.Many2one('farmer.cropping.request', string='Crop Request', readonly=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True, tracking=True)
    crop_request_transaction_ids = fields.Many2many(
        'crop.request.transaction', 
        relation='croprequest_wizard_transaction_rel', 
        # compute='_compute_reservation_ids', 
        string='Transactions associated to this Crop Request',
        # domain=[('project_id', 'in', lambda self: self.project_id.id)] 
        # store=True
        tracking=True
    )

    project_transaction_ids = fields.Many2many(
        'crop.request.transaction', 
        relation='project_wizard_transaction_rel', 
        # compute='_compute_reservation_ids', 
        string='Transactions associated to this Crop Request Project',
        # domain=[('project_id', 'in', lambda self: self.project_id.id)] 
        # store=True
        tracking=True
    )    

    def action_create_requisitions(self):
        # raise UserError(_( f'Lista de IDs: {self.crop_request_transaction_ids}' ))
        transaction_ids = []
        id_field_name = ''
        id_value = ''
        
        if self.usar_tareas:
            transaction_ids = self.project_transaction_ids
            id_field_name = 'project_id'
            id_value = self.project_id.id            
        else:
            transaction_ids = self.crop_request_transaction_ids
            id_field_name = 'farmer_request_id'
            id_value = self.farmer_request_id.id               

        list_ids = []
        for transaction in transaction_ids:
            list_ids.append(transaction.id)

        # Requisición:
        requisition_id = self.env['material.purchase.requisition'].search([(id_field_name, '=', id_value)]).id

        for id in list_ids:
            # ============= Insertando las líneas de la requisición ============= #
            my_id = self.env['crop.request.transaction'].browse(id).id
            transaction_obj = self.env['crop.request.transaction'].search([('id', '=', my_id)])
            type = transaction_obj.type

            transacion_model = ''
            transacion_model_id = ''
            transacion_model_field_name = ''

            # raise UserError(_(f'Tipo de Transacción: {type}'))
            requisition_line_obj = ''
            crop_request_transaction_obj = ''

            if type == 'equipment_reservation':                
                equipment_reservation_id = transaction_obj.equipment_reservation_id.id
                transacion_model = 'equipment.reservation'
                transacion_model_id = equipment_reservation_id
                transacion_model_field_name = 'equipment_reservation_id'                
                # Equipment Lines:
                equipment_reservation_ids = self.env['equipment.reservation'].search([('id', '=', equipment_reservation_id)]).equipment_reservation_ids
                for line in equipment_reservation_ids:
                    requisition_type = 'internal' # <------- 'internal','Requisición Interna'
                    if line.quantity > line.qty_available:
                        requisition_type = 'tender' # <------- 'tender','Licitación de Compra
                    
                    crop_request_transaction_line_id = line.id

                    requisition_line_obj = self.env['material.purchase.requisition.line'].create({
                        'requisition_id': requisition_id,
                        'crop_request_transaction_id': my_id,
                        'crop_request_transaction_line_id': crop_request_transaction_line_id,
                        'requisition_type': requisition_type,
                        'product_id': line.product_id.id,
                        'description': line.product_id.name,
                        'qty': line.quantity,
                        'qty_available': line.qty_available,
                        'free_qty': line.product_id.free_qty,
                        'uom': line.product_id.product_tmpl_id.uom_id.id,
                    })      

                    # ====================================================================================== #
                    # ================ Inicio de Funciones que agregan las Analytic Account ================ #
                    # ====================================================================================== #
                    # analytic_account_id_1 = task_analytic_account_id.parent_id.id # <--- Finca
                    # Finca:
                    analytic_account_id_1 = self.env['agriculture.fincas'].search([('id', '=', self.farmer_request_id.finca_id.id)]).analytic_account_id.id
                    analytic_account_id_2 = False

                    # Crop Request Transaction Analytic Account: 
                    crop_transaction_analytic_account_obj = False
                    # Crop Request Transaction Object:
                    crop_request_transaction_obj = self.env['crop.request.transaction'].search([(transacion_model_field_name, '=', transacion_model_id)])
                    if self.usar_tareas:
                        # Analytic Account de la Actividad / Tarea:
                        task_analytic_account_id = crop_request_transaction_obj.task_id.analytic_account_id
                        analytic_account_id_2 = task_analytic_account_id.id # <--- Actividad
                    else:
                        # Creando Centro de Costo para la actitivad / tarea (Crop Request Transaction):
                        crop_transaction_number = self.env[transacion_model].search([('id', '=', transacion_model_id)]).number
                        crop_transaction_analytic_account_obj = self.env['account.analytic.account'].create({
                            'name': f'{crop_request_transaction_obj.farmer_request_id.number} / {crop_transaction_number}',
                            'parent_id': analytic_account_id_1,
                            'is_parent_category': False,
                            
                            'finca_id': self.farmer_request_id.finca_id.id,
                            'crop_request_transaction_id': crop_request_transaction_obj.id,  
                            # Tipo:
                            'type': 'activity'
                        })                            
                        analytic_account_id_2 = crop_transaction_analytic_account_obj.id

                    parcel_obj = self.env['agriculture.parcelas'].search([('id', '=', self.farmer_request_id.parcel_id.id)])
                    analytic_account_id_3 = False
                    analytic_account_id_4 = False

                    if self.farmer_request_id.division_terreno == 'parcel':
                        # Lote / Parcela:
                        analytic_account_id_3 = parcel_obj.analytic_account_id.id
                    elif self.farmer_request_id.division_terreno == 'plank':
                        # Lote / Parcela:
                        analytic_account_id_3 = parcel_obj.analytic_account_id.id   
                        # Tablón:
                        analytic_account_id_4 = self.env['agriculture.tablon'].search([('id', '=', self.farmer_request_id.tablon_id.id)]).analytic_account_id.id

                    if crop_transaction_analytic_account_obj != False:
                        parcel_analytic_account_obj = self.env['account.analytic.account'].search([
                            ('finca_id', '=', self.farmer_request_id.finca_id.id),
                            ('parcel_id', '=', self.farmer_request_id.parcel_id.id),
                            ('type', '=', 'parcel')
                        ])
                        parcel_analytic_account_obj.write({
                            'crop_request_transaction_ids': [
                                (4, crop_request_transaction_obj.id, 0)
                            ]                                     
                        })

                    requisition_line_obj.write({
                        'analytic_account_id_1': analytic_account_id_1,
                        'analytic_account_id_2': analytic_account_id_2,
                        'analytic_account_id_3': analytic_account_id_3,
                        'analytic_account_id_4': analytic_account_id_4
                    })            
                    # ====================================================================================== #
                    # ================ Fin de Funciones que agregan las Analytic Account ================ #
                    # ====================================================================================== # 
                                    
            if type == 'labour_management':
                labour_management_id = transaction_obj.labour_management_id.id
                transacion_model = 'labour.management'
                transacion_model_id = labour_management_id
                transacion_model_field_name = 'labour_management_id'                
                # Labour Management:
                product_id = self.env['product.product'].search([('mano_de_obra', '=', True)], limit=1)
                reservation_type = self.env['labour.management'].search([('id', '=', labour_management_id)]).reservation_type
                
                '''
                labour_employee_ids = self.env['labour.management'].search([('id', '=', labour_management_id)]).labour_employee_ids
                quantity = len(labour_employee_ids)
                '''
                employee_ids = self.env['labour.management'].search([('id', '=', labour_management_id)]).employee_ids
                # quantity = len(employee_ids)                
                quantity = 1

                '''
                requisition_type = ''
                if reservation_type == 'own':
                    requisition_type = 'internal' # <------- 'internal','Requisición Interna'
                else:
                    requisition_type = 'tender' # <------- 'tender','Licitación de Compra                
                '''
                requisition_type = 'tender' # <------- 'tender','Licitación de Compra

                requisition_line_obj = self.env['material.purchase.requisition.line'].create({
                    'requisition_id': requisition_id,
                    'crop_request_transaction_id': my_id,
                    'requisition_type': requisition_type,
                    'product_id': product_id.id,
                    'description': product_id.name,
                    'qty': quantity,
                    'qty_available': quantity,
                    'free_qty': quantity,
                    'uom': product_id.product_tmpl_id.uom_id.id,
                }) 

                # ====================================================================================== #
                # ================ Inicio de Funciones que agregan las Analytic Account ================ #
                # ====================================================================================== #
                # analytic_account_id_1 = task_analytic_account_id.parent_id.id # <--- Finca
                # Finca:
                analytic_account_id_1 = self.env['agriculture.fincas'].search([('id', '=', self.farmer_request_id.finca_id.id)]).analytic_account_id.id
                analytic_account_id_2 = False

                # Crop Request Transaction Analytic Account: 
                crop_transaction_analytic_account_obj = False
                # Crop Request Transaction Object:
                crop_request_transaction_obj = self.env['crop.request.transaction'].search([(transacion_model_field_name, '=', transacion_model_id)])
                if self.usar_tareas:
                    # Analytic Account de la Actividad / Tarea:
                    task_analytic_account_id = crop_request_transaction_obj.task_id.analytic_account_id
                    analytic_account_id_2 = task_analytic_account_id.id # <--- Actividad
                else:
                    # Creando Centro de Costo para la actitivad / tarea (Crop Request Transaction):
                    crop_transaction_number = self.env[transacion_model].search([('id', '=', transacion_model_id)]).number
                    crop_transaction_analytic_account_obj = self.env['account.analytic.account'].create({
                        'name': f'{crop_request_transaction_obj.farmer_request_id.number} / {crop_transaction_number}',
                        'parent_id': analytic_account_id_1,
                        'is_parent_category': False,
                        
                        'finca_id': self.farmer_request_id.finca_id.id,
                        'crop_request_transaction_id': crop_request_transaction_obj.id,  
                        # Tipo:
                        'type': 'activity'
                    })                            
                    analytic_account_id_2 = crop_transaction_analytic_account_obj.id

                parcel_obj = self.env['agriculture.parcelas'].search([('id', '=', self.farmer_request_id.parcel_id.id)])
                analytic_account_id_3 = False
                analytic_account_id_4 = False

                if self.farmer_request_id.division_terreno == 'parcel':
                    # Lote / Parcela:
                    analytic_account_id_3 = parcel_obj.analytic_account_id.id
                elif self.farmer_request_id.division_terreno == 'plank':
                    # Lote / Parcela:
                    analytic_account_id_3 = parcel_obj.analytic_account_id.id   
                    # Tablón:
                    analytic_account_id_4 = self.env['agriculture.tablon'].search([('id', '=', self.farmer_request_id.tablon_id.id)]).analytic_account_id.id

                if crop_transaction_analytic_account_obj != False:
                    parcel_analytic_account_obj = self.env['account.analytic.account'].search([
                        ('finca_id', '=', self.farmer_request_id.finca_id.id),
                        ('parcel_id', '=', self.farmer_request_id.parcel_id.id),
                        ('type', '=', 'parcel')
                    ])
                    parcel_analytic_account_obj.write({
                        'crop_request_transaction_ids': [
                            (4, crop_request_transaction_obj.id, 0)
                        ]                                     
                    })

                requisition_line_obj.write({
                    'analytic_account_id_1': analytic_account_id_1,
                    'analytic_account_id_2': analytic_account_id_2,
                    'analytic_account_id_3': analytic_account_id_3,
                    'analytic_account_id_4': analytic_account_id_4
                })            
                # ====================================================================================== #
                # ================ Fin de Funciones que agregan las Analytic Account ================ #
                # ====================================================================================== # 

            if type == 'crop_material_management':
                crop_material_id = transaction_obj.crop_material_id.id
                transacion_model = 'crop.material.management'
                transacion_model_id = crop_material_id
                transacion_model_field_name = 'crop_material_id'                
                # Crop Material Management Lines:
                crop_material_ids = self.env['crop.material.management'].search([('id', '=', crop_material_id)]).crop_material_ids
                for line in crop_material_ids:
                    requisition_type = 'internal' # <------- 'internal','Requisición Interna'
                    if line.quantity > line.qty_available:
                        requisition_type = 'tender' # <------- 'tender','Licitación de Compra
                    
                    crop_request_transaction_line_id = line.id

                    requisition_line_obj = self.env['material.purchase.requisition.line'].create({
                        'requisition_id': requisition_id,
                        'crop_request_transaction_id': my_id,
                        'crop_request_transaction_line_id': crop_request_transaction_line_id,
                        'requisition_type': requisition_type,
                        'product_id': line.product_id.id,
                        'description': line.product_id.name,
                        'qty': line.quantity,
                        'qty_available': line.qty_available,
                        'free_qty': line.product_id.free_qty,
                        'uom': line.product_id.product_tmpl_id.uom_id.id,
                    })  

                    # ====================================================================================== #
                    # ================ Inicio de Funciones que agregan las Analytic Account ================ #
                    # ====================================================================================== #
                    # analytic_account_id_1 = task_analytic_account_id.parent_id.id # <--- Finca
                    # Finca:
                    analytic_account_id_1 = self.env['agriculture.fincas'].search([('id', '=', self.farmer_request_id.finca_id.id)]).analytic_account_id.id
                    analytic_account_id_2 = False

                    # Crop Request Transaction Analytic Account: 
                    crop_transaction_analytic_account_obj = False
                    # Crop Request Transaction Object:
                    crop_request_transaction_obj = self.env['crop.request.transaction'].search([(transacion_model_field_name, '=', transacion_model_id)])
                    if self.usar_tareas:
                        # Analytic Account de la Actividad / Tarea:
                        task_analytic_account_id = crop_request_transaction_obj.task_id.analytic_account_id
                        analytic_account_id_2 = task_analytic_account_id.id # <--- Actividad
                    else:
                        # Creando Centro de Costo para la actitivad / tarea (Crop Request Transaction):
                        crop_transaction_number = self.env[transacion_model].search([('id', '=', transacion_model_id)]).number
                        crop_transaction_analytic_account_obj = self.env['account.analytic.account'].create({
                            'name': f'{crop_request_transaction_obj.farmer_request_id.number} / {crop_transaction_number}',
                            'parent_id': analytic_account_id_1,
                            'is_parent_category': False,
                            
                            'finca_id': self.farmer_request_id.finca_id.id,
                            'crop_request_transaction_id': crop_request_transaction_obj.id,  
                            # Tipo:
                            'type': 'activity'
                        })                            
                        analytic_account_id_2 = crop_transaction_analytic_account_obj.id

                    parcel_obj = self.env['agriculture.parcelas'].search([('id', '=', self.farmer_request_id.parcel_id.id)])
                    analytic_account_id_3 = False
                    analytic_account_id_4 = False

                    if self.farmer_request_id.division_terreno == 'parcel':
                        # Lote / Parcela:
                        analytic_account_id_3 = parcel_obj.analytic_account_id.id
                    elif self.farmer_request_id.division_terreno == 'plank':
                        # Lote / Parcela:
                        analytic_account_id_3 = parcel_obj.analytic_account_id.id   
                        # Tablón:
                        analytic_account_id_4 = self.env['agriculture.tablon'].search([('id', '=', self.farmer_request_id.tablon_id.id)]).analytic_account_id.id

                    if crop_transaction_analytic_account_obj != False:
                        parcel_analytic_account_obj = self.env['account.analytic.account'].search([
                            ('finca_id', '=', self.farmer_request_id.finca_id.id),
                            ('parcel_id', '=', self.farmer_request_id.parcel_id.id),
                            ('type', '=', 'parcel')
                        ])
                        parcel_analytic_account_obj.write({
                            'crop_request_transaction_ids': [
                                (4, crop_request_transaction_obj.id, 0)
                            ]                                     
                        })

                    requisition_line_obj.write({
                        'analytic_account_id_1': analytic_account_id_1,
                        'analytic_account_id_2': analytic_account_id_2,
                        'analytic_account_id_3': analytic_account_id_3,
                        'analytic_account_id_4': analytic_account_id_4
                    })            
                    # ====================================================================================== #
                    # ================ Fin de Funciones que agregan las Analytic Account ================ #
                    # ====================================================================================== #                                 

            # Cambiando el estado de la transacción a 'Sent to Purchase Requisition':
            self.env[transacion_model].search([('id', '=', transacion_model_id)]).write({
                'state': 'sent_to_purchase_requisition'
            })

            crop_request_transaction_obj = self.env['crop.request.transaction'].search([(transacion_model_field_name, '=', transacion_model_id)])
            crop_request_transaction_obj.write({
                'state': 'sent_to_purchase_requisition'
            })
                                  
    '''
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    tasks_ids = fields.Many2many('project.task', relation='croprequest_wizard_task_rel', compute='_compute_tasks_ids', string='Tasks associated to this project', store=True)
    reservation_ids = fields.Many2many(
        'equipment.reservation', 
        relation='croprequest_wizard_reservation_rel', 
        # compute='_compute_reservation_ids', 
        string='Equipment Reservations associated to this project',
        # domain=[('task_id', 'in', lambda self: self.tasks_ids.ids)] 
        # store=True
    )
    
    @api.depends('project_id.task_ids')
    def _compute_tasks_ids(self):
        for rec in self:
            rec.tasks_ids = self.env['project.task'].search([('project_id', '=', rec.project_id.id)])

    @api.depends('project_id.task_ids')
    def _compute_reservation_ids(self):
        for rec in self:
            rec.reservation_ids = self.env['equipment.reservation'].search([('task_id', 'in', rec.tasks_ids.ids)])        
               
    '''