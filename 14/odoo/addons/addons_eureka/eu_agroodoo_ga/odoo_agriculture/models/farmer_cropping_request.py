# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError

class FarmerCroppingRequest(models.Model):
    _name = 'farmer.cropping.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = "Crop Requests"
    _rec_name = 'number'

    number = fields.Char(
        string='Number',
        readonly=True,
        copy=False,
        tracking=True
    )
    # name = fields.Char(
    #     string='Name',
    #     required=True
    # )
    
    usar_tareas = fields.Boolean(
        string='Use Activities Template',
        required=False,
        tracking=True
    )

    description = fields.Text(
        string='Description',
        tracking=True
    )
    internal_note = fields.Text(
        string='Internal Notes',
        tracking=True
    )
    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done','Done'),
        ('cancel','Cancel')
        ],
        string="State",
        default='new',
        # required=True,
        tracking=True
    )
    start_date = fields.Date(
        string='Start Date',
        # required=True,
        tracking=True
    )
    end_date = fields.Date(
        string='End Date',
        # required=True,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
        tracking=True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Supervisor",
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        copy=False,
        tracking=True
    )
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisition', 
        copy=False,
        tracking=True
    )

    responsible_user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    crop_ids = fields.Many2one(
        'farmer.location.crops',
        string='Crop',
        required=True,
        tracking=True
    )

    division_terreno = fields.Selection([
        ('none', 'None'),
        ('parcel', 'Parcel'),
        ('plank', 'Plank'),
        ],
        default='none',
        string="Land Division",
        required=True,
        tracking=True
    )    

    finca_id = fields.Many2one(
        'agriculture.fincas',
        string="Farm",
        required=True,
        tracking=True
    )    

    parcel_id = fields.Many2one(
        'agriculture.parcelas',
        string="Parcel",
        required=False,
        tracking=True
    )

    tablon_id = fields.Many2one(
        'agriculture.tablon',
        string="Plank",
        required=False,
        tracking=True
    )

    partner_id = fields.Many2one(
        related='finca_id.partner_id',
        string="Farmer",
        readonly=True,
        tracking=True
    )        

    equipment_count = fields.Integer(
        compute='_compute_equipment_counter',
        string="Equipment Count",
        tracking=True
    )

    # ==================================================================================== #
    # Workday Planning:
    cost_sheet_id = fields.Many2one('agriculture.cost.sheet', string='Workday Planning', tracking=True)
    cost_sheet_count = fields.Integer(
        compute='_compute_cost_sheet_count',
        string="Workday Planning Count",
        tracking=True
    )

    # ==================================================================================== #
    # Crop Request (Sin usar plantilla de Tareas)
    requisition_ids = fields.One2many('material.purchase.requisition', 'farmer_request_id', string='Requisitions (Crop Request)', tracking=True)
    requisition_count = fields.Integer(
        compute='_compute_requisition_count',
        string="Crop Request Requisition Count",
        tracking=True
    )  

    # ==================================================================================== #
    # Project (Usando plantilla de Tareas)
    project_requisition_ids = fields.One2many('material.purchase.requisition', 'project_id', string='Requisitions (Project)')
    project_requisition_count = fields.Integer(
        compute='_compute_project_requisition_count',
        string="Project Requisition Count",
        tracking=True
    )                

    # ==================================================================================== #
    equipment_reservation_ids = fields.One2many('equipment.reservation', 'farmer_request_id', string='Equipment Reservations', tracking=True)
    equipment_reservation_count = fields.Integer(
        compute='_compute_equipment_reservation_counter',
        string="Reservations",
        tracking=True
    )        
    
    # ==================================================================================== #
    labour_ids = fields.One2many('labour.management', 'farmer_request_id', string='Labours', tracking=True)
    labour_count = fields.Integer(
        compute='_compute_labour_counter',
        string="Labours",
        tracking=True
    ) 

    # ==================================================================================== #
    maintenance_request_ids = fields.One2many('maintenance.request', 'farmer_request_id', string='Maintenance Requests', tracking=True)
    maintenance_request_count = fields.Integer(
        compute='_compute_maintenance_request_counter',
        string="Maintenance Request Count",
        tracking=True
    )    

    # ==================================================================================== #
    crop_material_management_ids = fields.One2many('crop.material.management', 'farmer_request_id', string='Crop Material Managements', tracking=True)
    crop_material_management_count = fields.Integer(
        compute='_compute_crop_material_management_counter',
        string="Crop Material Management Count",
        tracking=True
    )        

    project_count = fields.Integer(
        compute='_compute_project_counter',
        string="Project Count",
        tracking=True
    )

    @api.depends('project_id')
    def _compute_project_counter(self):
        for rec in self:
            # rec.project_count = self.env['project.project'].search_count([('id', 'in', self.project_id.ids)])
            rec.project_count = self.env['project.project'].search_count([('custom_request_id', '=', rec.id)])

    # ==================================================================================== #
    @api.depends('cost_sheet_id')
    def _compute_cost_sheet_count(self):
        for rec in self:
            rec.cost_sheet_count = self.env['agriculture.cost.sheet'].search_count([('farmer_request_id', '=', self.id)])

    # ==================================================================================== #
    @api.depends('requisition_ids')
    def _compute_requisition_count(self):
        for rec in self:
            requisition_line_ids = self.env['material.purchase.requisition'].search([('farmer_request_id', '=', self.id)]).requisition_line_ids
            rec.requisition_count = len(requisition_line_ids)
            
    # ==================================================================================== #
    @api.depends('project_requisition_ids')
    def _compute_project_requisition_count(self):
        for rec in self:
            requisition_line_ids = self.env['material.purchase.requisition'].search([('project_id', '=', self.project_id.id)]).requisition_line_ids
            rec.project_requisition_count = len(requisition_line_ids)

    # ==================================================================================== #
    @api.depends('equipment_reservation_ids')
    def _compute_equipment_reservation_counter(self):
        for rec in self:
            rec.equipment_reservation_count = self.env['equipment.reservation'].search_count([('farmer_request_id', '=', self.id)])

    # ==================================================================================== #
    @api.depends('labour_ids')
    def _compute_labour_counter(self):
        for rec in self:
            rec.labour_count = self.env['labour.management'].search_count([('farmer_request_id', '=', self.id)])

    # ==================================================================================== #
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_request_counter(self):
        for rec in self:
            rec.maintenance_request_count = self.env['maintenance.request'].search_count([('farmer_request_id', '=', self.id)])

    # ==================================================================================== #
    @api.depends('crop_material_management_ids')
    def _compute_crop_material_management_counter(self):
        for rec in self:
            rec.crop_material_management_count = self.env['crop.material.management'].search_count([('farmer_request_id', '=', rec.id)])

    def _compute_equipment_counter(self):
        equipments = []
        for rec in self:
            rec.equipment_count = 0 # odoo13
            for crop in rec.crop_ids:
                for crop_temp in crop.crop_task_ids:
                    for equipment in crop_temp.equipment_ids:
                        equipments.append(equipment.id)
                        rec.equipment_count = self.env['maintenance.equipment'].search_count([('id','in', equipments)])

    # @api.multi #odoo13
    def view_project(self):
        action = self.env.ref('odoo_agriculture.action_view_form_task_project_crop_request').read()[0]
        action['domain'] = [('project_id', '=', self.project_id.id)]  
        action['context'] = {
            'default_project_id': self.project_id.id
        }          
        return action 
        
    # @api.multi #odoo13
    def view_project_request(self):
        action = self.env.ref('odoo_agriculture.action_view_farmer_cropping_agriculture_task').read()[0]
        action['domain'] = [('project_id', '=', self.project_id.id)]
        action['context'] = {
            'default_project_id': self.project_id.id
        }
        # raise UserError(_(type(action['context'])))
    
        # action = self.env.ref('odoo_agriculture.action_view_farmer_cropping_project').read()[0]
        # action['domain'] = [('id','in', self.project_id.ids)]        
        return action

    # ========= Inicio de Métodos de Botones Inteligentes en caso de SÍ usar Tareas ========= #
    def view_requisition_request(self):
        # self.ensure_one()
        action = self.env.ref('odoo_agriculture.action_material_purchase_requisition_agriculture_crop_request')
        action = action.read()[0]

        # Farm Analytic Account:
        parent_analytic_account_id = self.finca_id.analytic_account_id.id
        
        id_field_name = ''
        id_value = ''        
        if self.usar_tareas:
            id_field_name = 'project_id'
            id_value = self.project_id.id                
        else:
            id_field_name = 'farmer_request_id'
            id_value = self.id     

        requisition = self.env['material.purchase.requisition'].search([(id_field_name, '=', id_value)])            
        requisition.write({
            'parent_analytic_account_id': parent_analytic_account_id,
            'analytic_account_header_id_1': parent_analytic_account_id,
        })

        # raise UserError(_(farm_analytic_account_id))
        hide_header_analytic_account = 0
        required_header_analytic_account = 1

        if self.usar_tareas:
            hide_header_analytic_account = 1
            required_header_analytic_account = 0

        farm_readonly = 0
        activity_readonly = 0

        parcel_readonly = 1
        parcel_required = 0

        plank_readonly = 1
        plank_required = 0

        if self.division_terreno == 'parcel':
            if self.usar_tareas:
                parcel_required = 0   
                plank_required = 0

                farm_readonly = 1
                activity_readonly = 1
                parcel_readonly = 1
                plank_readonly = 1                
            else:
                parcel_required = 1   
                plank_required = 0
            
                parcel_readonly = 0
                plank_readonly = 1 
        
        elif self.division_terreno == 'plank':
            if self.usar_tareas:
                parcel_required = 0   
                plank_required = 0     

                farm_readonly = 1
                activity_readonly = 1
                parcel_readonly = 1
                plank_readonly = 1                          
            else:
                plank_required = 1
                parcel_required = 1

                parcel_readonly = 0
                plank_readonly = 0

        if self.usar_tareas:
            action['domain'] = [('project_id', '=', self.project_id.id)]
            action['context'] = {
                'default_project_id': self.project_id.id,
                'default_parent_analytic_account_id': parent_analytic_account_id,

                'hide_header_analytic_account': hide_header_analytic_account,
                'required_header_analytic_account': required_header_analytic_account,

                'farm_readonly': farm_readonly,
                'activity_readonly': activity_readonly,
                'parcel_readonly': parcel_readonly,
                'plank_readonly': plank_readonly,

                'parcel_required': parcel_required,
                'plank_required': plank_required,
            }
        else:
            action['domain'] = [('farmer_request_id', '=', self.id)]
            action['context'] = {
                'default_farmer_request_id': self.id,
                'default_parent_analytic_account_id': parent_analytic_account_id,

                'hide_header_analytic_account': hide_header_analytic_account,
                'required_header_analytic_account': required_header_analytic_account,
                
                'farm_readonly': farm_readonly,
                'activity_readonly': activity_readonly,                
                'parcel_readonly': parcel_readonly,
                'plank_readonly': plank_readonly,

                'parcel_required': parcel_required,
                'plank_required': plank_required,
            }

        return action

    def view_equipment_reservation(self):
        action = self.env.ref('odoo_agriculture.action_equipment_management').read()[0]
        action['domain'] = [('farmer_request_id', '=', self.id)]  
        action['context'] = {
            'default_farmer_request_id': self.id,
            'default_usar_tareas': False
        }          
        return action      

    def view_labour_management(self):
        action = self.env.ref('odoo_agriculture.action_labour_management').read()[0]
        action['domain'] = [('farmer_request_id', '=', self.id)]  
        action['context'] = {
            'default_farmer_request_id': self.id,
            'default_usar_tareas': False
        }        
        return action   

    def view_crop_material_management(self):
        action = self.env.ref('odoo_agriculture.action_crop_material_management').read()[0]
        action['domain'] = [('farmer_request_id', '=', self.id)]  
        action['context'] = {
            'default_farmer_request_id': self.id,
            'default_usar_tareas': False
        }              
        return action   

    def view_maintenance_request(self):
        action = self.env.ref('odoo_agriculture.hr_equipment_request_agriculture_action').read()[0]
        action['domain'] = [('farmer_request_id', '=', self.id)]  
        action['context'] = {
            'default_farmer_request_id': self.id,
            'default_usar_tareas': False
        }                
        return action   

    def view_cost_sheet(self):
        action = self.env.ref('odoo_agriculture.action_agriculture_cost_sheet').read()[0]
        action['domain'] = [('farmer_request_id', '=', self.id)]  
        
        hide_header_analytic_account = 0
        required_header_analytic_account = 1

        if self.usar_tareas:
            hide_header_analytic_account = 1
            required_header_analytic_account = 0

        farm_readonly = 0

        parcel_readonly = 1
        parcel_required = 0

        plank_readonly = 1
        plank_required = 0

        if self.division_terreno == 'parcel':
            parcel_required = 1   
            plank_required = 0
        
            parcel_readonly = 1
            plank_readonly = 1 
        
        elif self.division_terreno == 'plank':
            plank_required = 1
            parcel_required = 1

            parcel_readonly = 1
            plank_readonly = 1
        
        
        action['context'] = {
            'default_farmer_request_id': self.id,

            'hide_header_analytic_account': hide_header_analytic_account,
            'required_header_analytic_account': required_header_analytic_account,

            'farm_readonly': farm_readonly,
            'parcel_readonly': parcel_readonly,
            'plank_readonly': plank_readonly,

            'parcel_required': parcel_required,
            'plank_required': plank_required,            
        }                
        return action           

    # ========= Fin de Métodos de Botones Inteligentes en caso de usar Tareas ========= #

    @api.model
    def create(self, vals): 
        # Verificando si existe un registro con la misma finca, parcela, tablón y períodos de fecha:
        crop_ids = vals.get('crop_ids')
        finca_id = vals.get('finca_id')
        parcel_id = vals.get('parcel_id')
        tablon_id = vals.get('tablon_id')
        start_date = vals.get('start_date')
        end_date = vals.get('end_date')

        # row_count = self.env['farmer.cropping.request'].search_count([
        #     ('crop_ids', '=', crop_ids),
        #     ('finca_id', '=', finca_id),
        #     ('parcel_id', '=', parcel_id),
        #     ('tablon_id', '=', tablon_id),
        #     ('start_date', '=', start_date),
        #     ('end_date', '=', end_date)
        # ])

        # raise UserError(_(f'Cantidad de regitros: {row_count}'))
        # raise UserError(_(f'Finca: {finca_id} - Parcela: {parcel_id} - Tablón: {tablon_id}'))

        # if row_count != 0:
        #     mensaje = ''
        #     if self.parcel_id == False and self.tablon_id == False:
        #         mensaje = 'Ya existe un registro con los siguientes datos ingresados: cultivo, finca y período de tiempo.'
        #     if self.parcel_id != False and self.tablon_id == False:
        #         mensaje = 'Ya existe un registro con los siguientes datos ingresados: cultivo, finca, parcela y período de tiempo.'
        #     if self.parcel_id != False and self.tablon_id != False:
        #         mensaje = 'Ya existe un registro con los siguientes datos ingresados: cultivo, finca, parcela, tablón y período de tiempo.'
        #     raise ValidationError(_(mensaje))
        # else:
        #     vals['number'] = self.env['ir.sequence'].next_by_code('farmer.cropping.request')
        #     vals['state'] = 'draft'
        #     return super(FarmerCroppingRequest,self).create(vals)

        vals['number'] = self.env['ir.sequence'].next_by_code('farmer.cropping.request')
        vals['state'] = 'draft'
        return super(FarmerCroppingRequest,self).create(vals)        


    def action_create_job_cost_sheet(self):
        # Consultando la plantilla del cultivo seleccionado y creando (duplicando) el proyecto del cultivo:
        crop_project_template = self.env['project.project'].search([('project_template', '=', True), ('crop_id', '=', self.crop_ids.id)])
        task_ids_template = crop_project_template.task_ids
        reservation_ids_template = task_ids_template.reservation_ids

        # if self.project_id == False:
        self.project_id = crop_project_template.copy({
            'name': f'{self.crop_ids.name}-{self.number}', 
            'company_id': self.company_id.id,
            'finca_id': self.finca_id.id,
            'project_template': False,
        })                  

        crop_obj = self.env['farmer.location.crops'].search([('id', '=', self.crop_ids.id)])
        cost_sheet_obj = self.env['agriculture.cost.sheet'].create({
            'farmer_request_id': self.id,
            'project_id': self.project_id.id,
            'workday_date': fields.Date.today()
        })
        self.cost_sheet_id = cost_sheet_obj.id

        parcel_id = False
        tablon_id = False
        # Determinando la División del Terreno:
        if self.division_terreno == 'parcel':
            parcel_id = self.parcel_id.id

        if self.division_terreno == 'plank':
            parcel_id = self.parcel_id.id
            tablon_id = self.tablon_id.id

        # Materials:
        crop_material_ids = crop_obj.crop_material_ids
        for line in crop_material_ids:
            operation_type = ''
            if line.quantity > line.qty_available:
                operation_type = 'purchase'
            else:
                operation_type = 'internal_requisition'

            self.env['agriculture.cost.sheet.lines'].create({
                'agriculture_cost_sheet_id': cost_sheet_obj.id,
                'operation_type': operation_type,
                'internal_type': 'material', 
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'description': line.product_id.name,
                'uom_id': line.uom_id.id,

                # Finca - Parcela - Tablón
                'finca_id': self.finca_id.id,
                'parcel_id': parcel_id,
                'tablon_id': tablon_id,

                'hours': '',
                'cost_unit': line.product_id.list_price,
                'actual_timesheet_hours': '',
                'cost_price_subtotal': line.product_id.list_price * line.quantity
            })

        # Labours:
        crop_labour_ids = crop_obj.crop_labour_ids
        for line in crop_labour_ids:
            # operation_type = ''
            # if line.quantity > line.qty_available:
            #     operation_type = 'purchase'
            # else:
            #     operation_type = 'internal_requisition'   
            operation_type = 'purchase'

            self.env['agriculture.cost.sheet.lines'].create({
                'agriculture_cost_sheet_id': cost_sheet_obj.id,
                'operation_type': operation_type,
                'internal_type': 'labour', 
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'description': line.product_id.name,
                'uom_id': line.uom_id.id,

                # Finca - Parcela - Tablón
                'finca_id': self.finca_id.id,
                'parcel_id': parcel_id,   
                'tablon_id': tablon_id,

                'hours': '',
                'cost_unit': line.product_id.list_price,
                'actual_timesheet_hours': '',
                'cost_price_subtotal': line.product_id.list_price * line.quantity
            })     

        # Equipments:
        crop_equipment_ids = crop_obj.crop_equipment_ids
        for line in crop_equipment_ids:
            # operation_type = ''
            # if line.quantity > line.qty_available:
            #     operation_type = 'purchase'
            # else:
            #     operation_type = 'internal_requisition'   
            operation_type = 'purchase'

            self.env['agriculture.cost.sheet.lines'].create({
                'agriculture_cost_sheet_id': cost_sheet_obj.id,
                'operation_type': operation_type,
                'internal_type': 'equipment', 
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'vehicle_id': line.vehicle_id.id,
                'description': line.product_id.name,
                'uom_id': line.uom_id.id,

                # Finca - Parcela - Tablón
                'finca_id': self.finca_id.id,
                'parcel_id': parcel_id,   
                'tablon_id': tablon_id,
                
                'hours': '',
                'cost_unit': line.product_id.list_price,
                'actual_timesheet_hours': '',
                'cost_price_subtotal': line.product_id.list_price * line.quantity
            })   

        # Overheads:
        crop_overhead_ids = crop_obj.crop_overhead_ids
        for line in crop_overhead_ids:
            # operation_type = ''
            # if line.quantity > line.qty_available:
            #     operation_type = 'purchase'
            # else:
            #     operation_type = 'internal_requisition'   
            operation_type = 'purchase'

            self.env['agriculture.cost.sheet.lines'].create({
                'agriculture_cost_sheet_id': cost_sheet_obj.id,
                'operation_type': operation_type,
                'internal_type': 'overhead', 
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'description': line.product_id.name,
                'reference': '',
                'uom_id': line.uom_id.id,

                # Finca - Parcela - Tablón
                'finca_id': self.finca_id.id,
                'parcel_id': parcel_id,   
                'tablon_id': tablon_id,

                'hours': '',
                'cost_unit': line.product_id.list_price,
                'actual_timesheet_hours': '',
                'cost_price_subtotal': line.product_id.list_price * line.quantity
            })      

        # Hired Services:
        crop_hired_service_ids = crop_obj.crop_hired_service_ids
        for line in crop_hired_service_ids:
            # operation_type = ''
            # if line.quantity > line.qty_available:
            #     operation_type = 'purchase'
            # else:
            #     operation_type = 'internal_requisition'   
            operation_type = 'purchase'

            self.env['agriculture.cost.sheet.lines'].create({
                'agriculture_cost_sheet_id': cost_sheet_obj.id,
                'operation_type': operation_type,
                'internal_type': 'hired_service', 
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'description': line.product_id.name,
                'reference': '',
                'partner_id': line.partner_id.id,
                'uom_id': line.uom_id.id,

                # Finca - Parcela - Tablón
                'finca_id': self.finca_id.id,
                'parcel_id': parcel_id,   
                'tablon_id': tablon_id,

                'hours': '',
                'cost_unit': line.product_id.list_price,
                'actual_timesheet_hours': '',
                'cost_price_subtotal': line.product_id.list_price * line.quantity
            })                                                

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_in_progress(self , vals=None): #odoo13
        # projects_delete = self.env['project.project'].search([('crop_id', '=', False), ('project_template', '=', False)])
        # UserError(_(f'Proyectos a eliminar: {projects_delete}'))
        self.write({'state': 'in_progress'})
        
        # ============= Creando proyecto ============= #
        '''
        project_id = self.env['project.project'].create(project_vals)        
        '''

        project_id = False        
        # raise UserError(_('Consultando la plantilla del cultivo seleccionado'))
        crop_ids = self.crop_ids.id
        usar_tareas = self.usar_tareas
        if usar_tareas:
            # Consultando la plantilla del cultivo seleccionado:
            crop_project_template = self.env['project.project'].search([('project_template', '=', True), ('crop_id', '=', crop_ids)])
            task_ids_template = crop_project_template.task_ids
            reservation_ids_template = task_ids_template.reservation_ids

            self.project_id = crop_project_template.copy({
                'name': self.number if self.number else '' + '-' + self.number if self.number else '',
                'company_id': self.company_id.id,
                'finca_id': self.finca_id.id,
                # 'alias_id': 1,
                # 'custom_request_id': self.id,
                'project_template': False,
                # 'task_ids': {
                  #  'reservation_ids': reservation_ids_template
                # }
            })

            project_id = self.project_id.id
            
            finca_id = self.finca_id.id
            farm_analytic_account_id = self.finca_id.analytic_account_id.id
            farm_name = self.finca_id.name    

            # =============== Actividades =============== #
            tasks = self.env['project.task'].search([('project_id', '=', project_id)])
            # raise UserError(_(f'Tasks: {tasks}'))
            if len(tasks) > 0:
                for task in tasks:
                    task_id = task.id
                    task_name = f'{task.name}'
                    # task_name = f'[{farm_name}] -> {task.name}'
                    # raise UserError(_(f'task: {task}'))

                    activity_analytic_account_obj = self.env['account.analytic.account'].search([
                        ('finca_id', '=', finca_id),
                        ('task_id', '=', task_id)
                    ])
                    if len(activity_analytic_account_obj) == 0:
                        # Creando Centro de Costo para la actitivad / tarea (su C.C padre será la finca seleccionada):
                        activity_analytic_account_obj = self.env['account.analytic.account'].create({
                            'name': task_name,
                            'parent_id': farm_analytic_account_id,
                            'is_parent_category': False,
                            
                            'finca_id': finca_id,
                            'task_id': task_id,
                            # Tipo:
                            'type': 'activity'
                        })    

                    # Asociando la Actividad con el Centro de Costo:
                    self.env['project.task'].search([('id', '=', task_id)]).write({            
                        'analytic_account_id': activity_analytic_account_obj.id
                    })     

                    # Determinando la División del Terreno:
                    # =============== Parcela o Tablón =============== #
                    # raise UserError(_(f'division_terreno: {self.division_terreno}'))
                    if self.division_terreno == 'parcel' or self.division_terreno == 'plank':
                        parcel_obj = self.parcel_id
                        parcel_id = parcel_obj.id
                        parcel_analytic_account_obj = self.env['account.analytic.account'].search([
                            ('finca_id', '=', finca_id),
                            ('parcel_id', '=', parcel_id),
                            ('type', '=', 'parcel')
                        ])
                        
                        # raise UserError(_(parcel_analytic_account_obj))

                        # Agregando Actividad al Many2many de Actividades de la Parcela:
                        parcel_analytic_account_obj.write({
                            'task_ids': [
                                (4, task_id, 0)
                            ]                                     
                        })

        # ============= Requisición ============= #
        # analytic_account_id = self.env['account.analytic.account'].search([])[-1].id
        requisiton_responsible_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1).id    
        # ============= Creando requisición ============= #
        parent_analytic_account_id = self.finca_id.analytic_account_id.id
        
        # analytic_use = 'header'
        # if self.usar_tareas:
        #     analytic_use = 'line'
        analytic_use = 'line'

        requisition_vals = {
            'analytic_use': analytic_use,
            'farmer_request_id': self.id,
            'project_id': project_id,
            'requisiton_responsible_id': requisiton_responsible_id,
            'partner_id': self.env.user.id,
            'parent_analytic_account_id': parent_analytic_account_id,
        }            
        requisition = self.env['material.purchase.requisition'].create(requisition_vals)

        # Eliminando los siguientes registros:
        self.env['crop.request.transaction'].search([('farmer_request_id', '=', False), ('task_id', '=', False)]).unlink()
    

    # @api.multi #odoo13
    def action_done(self):
        return self.write({'state': 'done'})

    # @api.multi #odoo13
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    # @api.multi #odoo13
    def action_reset_to_draft(self):
        return self.write({'state': 'draft'})

    # @api.multi #odoo13
    def action_show_records_requisition(self):
        action = self.env.ref('odoo_agriculture.action_crop_request_records_requisition').read()[0]
        action['context'] = {
            'default_farmer_request_id': self.id,
            'default_project_id': self.project_id.id,
            'default_usar_tareas': self.usar_tareas,
            'default_task_ids': self.project_id.task_ids.ids,
        }
        # raise UserError(_(f'IDs de las Tareas: {self.project_id.task_ids.ids}'))
        return action

    '''
    @api.onchange('division_terreno')
    def _onchange_division_terreno(self):
        if self.division_terreno == 'plank':
            self.parcel_id = ''
            self.finca_id = ''
            self.partner_id = ''

    @api.onchange('tablon_id')
    def _onchange_tablon_id(self):
        self.parcel_id = self.tablon_id.parcel_id
        self.finca_id = self.tablon_id.parcel_id.finca_id
        self.partner_id = self.tablon_id.parcel_id.finca_id.partner_id    
    '''