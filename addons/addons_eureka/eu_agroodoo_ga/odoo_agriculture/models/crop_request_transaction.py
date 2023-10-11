# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class CropRequestTransaction(models.Model):
    _name = 'crop.request.transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'project_id'
    _rec_name = 'task_id'

    # En caso de NO usar la plantilla del cultivo:
    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        copy=False,
        tracking=True
    )    

    # En caso de SÍ usar la plantilla del cultivo:
    task_id = fields.Many2one(
        'project.task',
        string="Task",
        copy=False,
        tracking=True
    )  

    project_id = fields.Many2one(
        'project.project',
        string="Project",
        related = "task_id.project_id",
        copy=False,
        tracking=True
    )             

    # Transacción para template:
    crop_project_template_id = fields.Many2one(
        'project.project',
        string='Crop Project Template',
        required=False,
        copy=False,
        tracking=True
    )   

    # ======================================================================== #

    type = fields.Selection([
        ('equipment_reservation', 'Equipment Reservation'),
        ('labour_management', 'Labour Management'),
        ('crop_material_management', 'Crop Material Management'),
        ('maintenance_request', 'Maintenance Request'),
    ], required=True, copy=False, tracking=True)

    equipment_reservation_id = fields.Many2one(
        'equipment.reservation',
        string='Equipment Reservation',
        ondelete='cascade',
        required=False,
        readonly=True,
        copy=False,
        tracking=True
    )    

    labour_management_id = fields.Many2one(
        'labour.management',
        string='Labour',
        ondelete='cascade',
        required=False,
        readonly=True,
        copy=False,
        tracking=True
    )    

    crop_material_id = fields.Many2one(
        'crop.material.management',
        string='Crop Material',
        ondelete='cascade',
        required=False,
        readonly=True,
        copy=False,
        tracking=True
    )

    maintenance_request_id = fields.Many2one(
        'maintenance.request', 
        string='Maintenance Request',
        ondelete='cascade',
        required=False,
        readonly=True,
        copy=False,
        tracking=True
    )

    state = fields.Selection(string='Status', 
        required=True, 
        # readonly=True, 
        tracking=True, selection=[
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('cancelled', 'Cancelled'),
            ('approved', 'Approved'),
            ('sent_to_purchase_requisition', 'Sent to Purchase Requisition'),
            ('added_from_cpt', 'Added from Crop Project Template'),
        ], 
        default='draft',
        # compute='_compute_state',
        # store=True
    )    

    # task_ids = fields.Many2many('project.task', 'crop_request_transaction_task_rel', 'crop_request_transaction_id', 'task_id')

    def name_get(self):
        list_name = []
        for rec in self:
            transaction_obj = self.env['crop.request.transaction'].search([('id', '=', rec.id)])
            type = rec.type

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

            name_record = ''
            if rec.farmer_request_id:
                name_record = f'{rec.farmer_request_id.number} / {number}'
            elif rec.crop_project_template_id:
                name_record = f'{rec.crop_project_template_id.name} / {number}'
            else:
                name_record = f'{rec.project_id.name} / {rec.task_id.name} / {number}'

            list_name.append((rec.id, name_record))
        return list_name


    # @api.depends('equipment_reservation_id', 'labour_management_id', 'crop_material_id', 'maintenance_request_id')
    '''
    def _compute_state(self):
        for rec in self:
            model = ''
            field = False

            if rec.type == 'equipment_reservation':
                model = 'equipment.reservation'
                field = rec.equipment_reservation_id
                
            if rec.type == 'labour_management':
                model = 'labour.management'
                field = rec.labour_management_id

            if rec.type == 'crop_material_management':
                model = 'crop.material.management'
                field = rec.crop_material_id

            if rec.type == 'maintenance_request':
                model = 'maintenance.request'
                field = rec.maintenance_request_id    

            id = field.id             
            new_state = self.env[model].search([('id', '=', id)]).state

            rec.state = new_state          
    '''