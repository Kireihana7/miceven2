# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LabourManagement(models.Model):
    _name = 'labour.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    @api.model
    def default_get(self, fields):
        res = super(LabourManagement, self).default_get(fields)
        res['task_id'] = self.env.context.get('default_task_id')
        res['farmer_request_id'] = self.env.context.get('default_farmer_request_id')
        res['crop_project_template_id'] = self.env.context.get('default_crop_project_template_id')
        return res

    number = fields.Char(
        string='Number',
        required=True,
        default=lambda self: _('New'),
        tracking=True
    )

    name = fields.Char(
        string='Name',
        tracking=True
        # required=True
    )    

    description = fields.Text(string='Description', tracking=True)

    # En caso de NO usar la plantilla del cultivo:
    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        required=False,
        tracking=True
    )    

    # En caso de SÍ usar la plantilla del cultivo:
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=False,
        tracking=True
    )        

    # Transacción para template:
    crop_project_template_id = fields.Many2one(
        'project.project',
        string='Crop Project Template',
        required=False,
        tracking=True
    )              
    
    reservation_type = fields.Selection(string='Reservation Type', 
        required=True, 
        tracking=True, 
        selection=[
            ('own', 'Own'),
            ('rented', 'Rented'),
    ])    

    supervisor_id = fields.Many2one('res.partner',
        string='Supervisor', tracking=True)

    responsible_user_id = fields.Many2one('res.partner',
        string='Responsible', tracking=True)

    start_date = fields.Datetime(
         string='Start Date',
         required=True,
         tracking=True
    )

    end_date = fields.Datetime(
         string='End Date',
         required=True,
         tracking=True
    )

    state = fields.Selection(string='Status', 
        required=True, 
        readonly=True, 
        tracking=True, selection=[
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('cancelled', 'Cancelled'),
            ('approved', 'Approved'),
            ('sent_to_purchase_requisition', 'Sent to Purchase Requisition'),
        ], 
        default='draft')    

    total_pay_amount = fields.Float(string='Total Pay Amount', required=True, tracking=True)

    labour_employee_ids = fields.One2many('labour.management.employee.lines', 'labour_management_id', 'Labours', copy=True, auto_join=True, tracking=True)
    employee_ids = fields.Many2many('hr.employee', 'labour_management_employee_rel', 'labour_management_id', 'employee_id', 'Labours', copy=True, auto_join=True, tracking=True)

    def action_request(self):
        self.state = 'requested'

    def action_approve(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.state = 'draft'    

    # ============================================================ #
    @api.constrains('total_pay_amount')
    def _check_total_pay_amount(self):
        if self.total_pay_amount <= 0:
            raise ValidationError(_('The Total Pay Amount must not be less or equal to 0.00.'))            

    @api.model    
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('labour.management') or _('New')        
        res = super(LabourManagement, self).create(vals)

        # Verificando si se usó la plantilla de tareas o no:    
        usar_tareas = self.env.context.get('default_usar_tareas')

        id_field_name = 'farmer_request_id'
        id_value = vals.get('farmer_request_id')
        if usar_tareas == True:
            id_field_name = 'task_id'
            id_value = vals.get('task_id')        

        # Último ID del modelo 'labour.management':
        last_labour_management_obj = self.env['labour.management'].search([])[-1]
        labour_management_id = last_labour_management_obj.id
        crop_project_template_id = last_labour_management_obj.crop_project_template_id.id

        # Insertando datos:
        self.env['crop.request.transaction'].create({
            id_field_name: id_value,
            'labour_management_id': labour_management_id,
            'crop_project_template_id': crop_project_template_id,
            'type': 'labour_management'
        })        
        
        return res      

class LabourManagementEmployeeLines(models.Model):
    _name = 'labour.management.employee.lines'
    
    labour_management_id = fields.Many2one(
        'labour.management',
        string='Labour',
        ondelete='cascade',
        required=True,
        index=True,
        readonly=True,
        tracking=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True
    )