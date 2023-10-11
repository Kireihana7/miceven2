# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def default_get(self, fields):
        res = super(Project, self).default_get(fields)
        res['crop_id'] = self.env.context.get('default_crop_id')
        return res    

    project_template = fields.Boolean(
        string="Project Template",
        tracking=True
    )

    crop_id = fields.Many2one(
        'farmer.location.crops',
        string='Crop',
        required=False,
        tracking=True
    )    

    finca_id = fields.Many2one(
        'agriculture.fincas',
        string='Farm',
        required=False,
        readonly=True,
        tracking=True
    )    

    custom_request_id = fields.Many2one(
        'farmer.cropping.request',
        string = 'Crop Request',
        tracking=True
    )
    crop_request_count = fields.Integer(
        compute='_compute_crop_request_counter',
        string="Crop Request Count",
        tracking=True
    )
    crop_count = fields.Integer(
        compute='_compute_crop_counter',
        store=True,
        string="Crop Count",
        tracking=True
    )

    # @api.multi #odoo13
    def action_crops_requests(self):
        action = self.env.ref('odoo_agriculture.action_farmer_cropping_request').read()[0]
        action['domain'] = [('project_id','in', self.ids)]
        return action

    def _compute_crop_request_counter(self):
        for rec in self:
            rec.crop_request_count = self.env['farmer.cropping.request'].search_count([('project_id', 'in', rec.ids)])

    # @api.multi #odoo13
    def action_crops(self):
        action = self.env.ref('odoo_agriculture.action_farmer_location_crop').read()[0]
        action['domain'] = [('id','=', self.custom_request_id.crop_ids.id)]
        return action

    def _compute_crop_counter(self):
        for rec in self:
            rec.crop_count = self.env['farmer.location.crops'].search_count([('id', '=', rec.custom_request_id.crop_ids.id)])

    #@api.model
    #def create(self, vals): 
        ##vals['number'] = self.env['ir.sequence'].next_by_code('project.project')
    #	return super(Project,self).create(vals)

    # {lambda self: self.crop_id.name}
    '''
    _sql_constraints = [
        ('unique_crop_id', 'unique(crop_id)', f'Ya existe una plantilla para este cultivo.')
    ]        
    '''
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class Task(models.Model):
    _inherit = "project.task"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string='Analytic Account',
        # required=True,
        readonly=True,
        domain=[('num_parents', '=', 1)],
        tracking=True
    )

    crop_incident_ids = fields.One2many(
        'crops.incident',
        'task_id',
        string='Crops Incident',
        tracking=True
    )
    animal_ids = fields.One2many(
        'crops.animals',
        'task_id',
        string="Animals",
        required=False,
        tracking=True
    )
    fleet_ids = fields.One2many(
        'crops.fleet',
        'task_id',
        string="Fleets",
        required=False,
        tracking=True
    )
    equipment_ids = fields.Many2many(
        'maintenance.equipment',
        string='Equipments',
        required=False,
        tracking=True
    )
    custom_request_id = fields.Many2one(
        'farmer.cropping.request',
        string = 'Crop Request',
        tracking=True
    )
    is_cropping_request = fields.Boolean(
        string='Is Cropping Request?',
        tracking=True
    )

    maintenance_request_ids = fields.One2many('maintenance.request', 'task_id', string='Maintenance Requests', tracking=True)

    # ======================================================== #
    requisition_count = fields.Integer(
        compute='_compute_requisition_counter',
        string="Requisiciones",
        tracking=True
    )

    reservation_count = fields.Integer(
        compute='_compute_reservation_counter',
        string="Reservations",
        tracking=True
    )    

    labour_count = fields.Integer(
        compute='_compute_labour_counter',
        string="Labours",
        tracking=True
    ) 

    crop_material_count = fields.Integer(
        compute='_compute_crop_material_count',
        string="Labours",
        tracking=True
    )     

    maintenance_request_count = fields.Integer(
        compute='_compute_maintenance_request_counter',
        string="Maintenance Request Count",
        tracking=True
    )       
    
    analytic_account_id_count = fields.Integer(
        compute='_compute_analytic_account_id_count',
        string="Analytic Account Count",
        tracking=True
    )            

    reservation_ids = fields.One2many('equipment.reservation', 'task_id', 'Reservations', tracking=True)
    labour_ids = fields.One2many('labour.management', 'task_id', 'Labours', tracking=True)    
    crop_material_ids = fields.One2many('crop.material.management', 'task_id', 'Crop Materials', tracking=True)    

    def copy(self, default=None):
        new_taks = self.env['project.task']
        for rec in self:
            # ================== Equipment Reservation ================== #
            new_reservations = self.env['equipment.reservation'] #  <---- Instancia vacía. Se lea agregan modelos con el +=
            for reservation in rec.reservation_ids:
                new_reservations += reservation.copy()

            # ================== Labour Management ================== #
            new_labour_managements = self.env['labour.management'] #  <---- Instancia vacía. Se lea agregan modelos con el +=
            for labour in rec.labour_ids:
                new_labour_managements += labour.copy()    
                
            # ================== Crop Material Management ================== #
            new_crop_material_management = self.env['crop.material.management'] #  <---- Instancia vacía. Se lea agregan modelos con el +=
            for crop_material in rec.crop_material_ids:
                new_crop_material_management += crop_material.copy()                                

            # Heredando el método copy:
            new_task = super(Task, rec).copy(default)

            # Equipment Reservation:
            new_reservations.write({
                'task_id': new_task.id
            })
            # Labour Management:
            new_labour_managements.write({
                'task_id': new_task.id
            })     
            # Crop Material Management:
            new_crop_material_management.write({
                'task_id': new_task.id
            })                        

            new_taks += new_task

        # Registrando Transacciones:        
        for i in new_taks:
            task_id = i.id
            # ================== Equipment Reservation ================== #
            new_reservations = self.env['equipment.reservation'].search([('task_id', '=', task_id)])
            if len(new_reservations) > 0:
                for j in new_reservations:
                    equipment_reservation_id = j.id
                    self.env['crop.request.transaction'].create({
                        'task_id': task_id,
                        'equipment_reservation_id': equipment_reservation_id,
                        'type': 'equipment_reservation',
                    })

            
            # ================== Labour Management ================== #
            new_labour_managements = self.env['labour.management'].search([('task_id', '=', task_id)])
            if len(new_labour_managements) > 0:
                for j in new_labour_managements:
                    labour_management_id = j.id
                    self.env['crop.request.transaction'].create({
                        'task_id': task_id,
                        'labour_management_id': labour_management_id,
                        'type': 'labour_management',
                    })

            # ================== Crop Material Management ================== #
            new_crop_material_management = self.env['crop.material.management'].search([('task_id', '=', task_id)])
            if len(new_crop_material_management) > 0:
                for j in new_crop_material_management:
                    crop_material_id = j.id
                    self.env['crop.request.transaction'].create({
                        'task_id': task_id,
                        'crop_material_id': crop_material_id,
                        'type': 'crop_material_management',
                    })
        # raise UserError(_(new_taks))
        return new_taks

    '''
    def copy(self, default=None):
        new_taks = self.env['project.task']
        for rec in self:
            new_reservations = self.env['equipment.reservation'] #  <---- Instancia vacía. Se lea agregan modelos con el +=
            for reservation in rec.reservation_ids:
                new_reservations += reservation.copy()

            new_task = super(Task, rec).copy(default)
            new_reservations.write({
                'task_id': new_task.id
            })
            new_taks += new_task
        return new_taks    
    '''

    def _compute_requisition_counter(self):
        for rec in self:
            rec.requisition_count = self.env['material.purchase.requisition'].search_count([('task_id', '=', rec.id)])    

    @api.depends('reservation_ids')
    def _compute_reservation_counter(self):
        for rec in self:
            rec.reservation_count = self.env['equipment.reservation'].search_count([('task_id', '=', rec.id)])

    @api.depends('labour_ids')
    def _compute_labour_counter(self):
        for rec in self:
            rec.labour_count = self.env['labour.management'].search_count([('task_id', '=', rec.id)])            


    @api.depends('crop_material_ids')
    def _compute_crop_material_count(self):
        for rec in self:
            rec.crop_material_count = self.env['crop.material.management'].search_count([('task_id', '=', rec.id)])            

    @api.depends('maintenance_request_ids')
    def _compute_maintenance_request_counter(self):
        for rec in self:
            rec.maintenance_request_count = self.env['maintenance.request'].search_count([('task_id', '=', rec.id)])


    @api.depends('analytic_account_id')
    def _compute_analytic_account_id_count(self):
        for rec in self:
            rec.analytic_account_id_count = self.env['account.analytic.account'].search_count([('task_id', '=', rec.id)])


    # ========= Inicio de Métodos de Botones Inteligentes en caso de NO usar Tareas ========= #
    def view_requisition_request(self):
        self.ensure_one()
        action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition')
        action = action.read()[0]
        action['domain'] = str([('task_id', '=', self.id)])
        return action

    def view_equipment_reservation(self):
        action = self.env.ref('odoo_agriculture.action_equipment_management').read()[0]
        action['domain'] = [('task_id', '=', self.id)]  
        
        default_crop_project_template_id = False
        if self.project_id.project_template:
            default_crop_project_template_id = self.project_id.id

        action['context'] = {
            'default_task_id': self.id,
            'default_usar_tareas': True,
            'default_crop_project_template_id': default_crop_project_template_id
        }        
        return action      

    def view_labour_management(self):
        action = self.env.ref('odoo_agriculture.action_labour_management').read()[0]
        action['domain'] = [('task_id', '=', self.id)]

        default_crop_project_template_id = False
        if self.project_id.project_template:
            default_crop_project_template_id = self.project_id.id

        action['context'] = {
            'default_task_id': self.id,
            'default_usar_tareas': True,
            'default_crop_project_template_id': default_crop_project_template_id
        }        
        return action      

    def view_crop_material_management(self):
        action = self.env.ref('odoo_agriculture.action_crop_material_management').read()[0]
        action['domain'] = [('task_id', '=', self.id)]

        default_crop_project_template_id = False
        if self.project_id.project_template:
            default_crop_project_template_id = self.project_id.id

        action['context'] = {
            'default_task_id': self.id,
            'default_usar_tareas': True,
            'default_crop_project_template_id': default_crop_project_template_id
        }        
        return action   

    def view_maintenance_request(self):
        action = self.env.ref('odoo_agriculture.hr_equipment_request_agriculture_action').read()[0]
        action['domain'] = [('task_id', '=', self.id)]

        default_crop_project_template_id = False
        if self.project_id.project_template:
            default_crop_project_template_id = self.project_id.id

        action['context'] = {
            'default_task_id': self.id,
            'default_usar_tareas': True,
            'default_crop_project_template_id': default_crop_project_template_id
        }
        return action   

    def action_create_analytic_account(self):
        # Creando Centro de Costo para la Finca:
        task_analytic_account_obj = self.env['account.analytic.account'].create({
            'name': self.name,
            'parent_id': False,
            'is_parent_category': False,
            # Agriculture:
            'task_id': self.id,
            # Tipo:
            'type': 'activity'
        })

        # Asociando la Finca con el Centro de Costo:
        self.write({
            # 'name': self.name,                
            'analytic_account_id': task_analytic_account_obj.id
        })

    def show_crop_project_template_transactions(self):
        action = self.env.ref('odoo_agriculture.action_crop_project_template_transactions').read()[0]
        action['context'] = {
            'default_crop_project_template_id': self.project_id.id,
            'default_task_id': self.id,
        }        
        return action        