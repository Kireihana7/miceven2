# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _  
from odoo.exceptions import UserError, ValidationError, Warning

class AgricultureWorkdaySpreadsheet(models.Model):
    _name = 'agriculture.workday.spreadsheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'  

    name = fields.Char(
        string='Name',
        default='New',
        required=True,
        tracking=True
    )

    agriculture_cost_sheet_id = fields.Many2one('agriculture.cost.sheet', string='Workday Planning', required=True, tracking=True)

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        readonly=True,
        tracking=True
    )       

    crop_id = fields.Many2one(
        'farmer.location.crops',
        string='Crop',
        required=True,
        tracking=True
    )

    finca_id = fields.Many2one(
        'agriculture.fincas',
        string="Farm",
        required=True,
        tracking=True
    )        

    # farmer_request_id = fields.Many2one(
    #     'farmer.cropping.request',
    #     string='Crop Request',
    #     # required=True,
    #     readonly=True,
    #     tracking=True
    # )       

    planning_date = fields.Date(
        string='Planning Date',
        required=True,
        tracking=True
    )    

    workday_date = fields.Date(
        string='Workday Date',
        required=True,
        tracking=True
    )    

    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)

    purchase_id = fields.Many2one('purchase.order', readonly=True, string='Purchase Order', tracking=True)
    cost_sheet_material_ids = fields.One2many(
        'agriculture.workday.spreadsheet.lines',
        'agriculture_workday_spreadsheet_id',
        string='Materials',
        domain=[('internal_type', '=', 'material')],
        copy=True, 
        auto_join=True,
        compute='_compute_lines',
        inverse='_inverse_lines',
        store=True,
        tracking=True
    )        

    cost_sheet_labour_ids = fields.One2many(
        'agriculture.workday.spreadsheet.lines',
        'agriculture_workday_spreadsheet_id',
        string='Labours',
        domain=[('internal_type', '=', 'labour')],
        compute='_compute_lines',
        inverse='_inverse_lines',
        store=True,
        tracking=True
    )       

    cost_sheet_equipment_ids = fields.One2many(
        'agriculture.workday.spreadsheet.lines',
        'agriculture_workday_spreadsheet_id',
        string='Equipments',
        domain=[('internal_type', '=', 'equipment')],
        compute='_compute_lines',
        inverse='_inverse_lines',
        store=True,
        tracking=True
    )            

    cost_sheet_overhead_ids = fields.One2many(
        'agriculture.workday.spreadsheet.lines',
        'agriculture_workday_spreadsheet_id',
        string='Overheads',
        domain=[('internal_type', '=', 'overhead')],
        compute='_compute_lines',
        inverse='_inverse_lines',
        store=True,
        tracking=True
    )    

    cost_sheet_hired_service_ids = fields.One2many(
        'agriculture.workday.spreadsheet.lines',
        'agriculture_workday_spreadsheet_id',
        string='Hired Services',
        domain=[('internal_type', '=', 'hired_service')],
        compute='_compute_lines',
        inverse='_inverse_lines',
        store=True,
        tracking=True
    )                   
    
    job_cost_details = fields.Char(
        string='Job Cost Details',
        tracking=True
    )

    amount_material_cost = fields.Float('Total Material Cost', compute='_compute_amount_material_cost', store=True)
    amount_labour_cost = fields.Float('Total Labour Cost', compute='_compute_amount_labour_cost', store=True)
    amount_equipment_cost = fields.Float('Total Equipment Cost', compute='_compute_amount_equipment_cost', store=True)
    amount_overhead_cost = fields.Float('Total Overhead Cost', compute='_compute_amount_overhead_cost', store=True)
    amount_hired_service_cost = fields.Float('Total Hired Service Cost', compute='_compute_amount_hired_service_cost', store=True)
    
    amount_total = fields.Float('Total Cost', compute='_compute_amount_total', store=True)

    state = fields.Selection([
            ('new', 'New'),
            ('draft', 'Draft'),
            ('executed', 'Executed'),
        ],
        string="State",
        default='new',
        # required=True,
        tracking=True
    )

    def action_execute(self):
        self.write({'state': 'executed'})

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            # 'analytic_account_id': self.analytic_account_id.id if self.analytic_use == 'header' else line.analytic_account_id.id,
            'product_id' : line.product_id.id,
            # 'product_uom_qty' : line.qty,
            'product_uom_qty' : line.quantity,
            # 'product_uom' : line.uom.id,
            'product_uom' : line.uom_id.id,
            'location_id' : self.location_id.id,
            'location_dest_id' : self.dest_location_id.id,
            'name' : line.product_id.name,
            'picking_type_id' : self.custom_picking_type_id.id,
            'picking_id' : stock_id.id,
            # 'custom_requisition_line_id' : line.id,
            'custom_cost_sheet_line_id': line.id,
            # 'company_id' : line.requisition_id.company_id.id,
            'company_id': self.company_id.id
        }
        return pick_vals

    @api.depends('cost_sheet_material_ids')
    def _compute_amount_material_cost(self):
        for rec in self:
            total = 0
            for line in rec.cost_sheet_material_ids:
                total += line.cost_price_subtotal
            rec.amount_material_cost = total

    @api.depends('cost_sheet_labour_ids')
    def _compute_amount_labour_cost(self):
        for rec in self:
            total = 0
            for line in rec.cost_sheet_labour_ids:
                total += line.cost_price_subtotal
            rec.amount_labour_cost = total

    @api.depends('cost_sheet_equipment_ids')
    def _compute_amount_equipment_cost(self):
        for rec in self:
            total = 0
            for line in rec.cost_sheet_equipment_ids:
                total += line.cost_price_subtotal
            rec.amount_equipment_cost = total

    @api.depends('cost_sheet_overhead_ids')
    def _compute_amount_overhead_cost(self):
        for rec in self:
            total = 0
            for line in rec.cost_sheet_overhead_ids:
                total += line.cost_price_subtotal
            rec.amount_overhead_cost = total

    @api.depends('cost_sheet_hired_service_ids')
    def _compute_amount_hired_service_cost(self):
        for rec in self:
            total = 0
            for line in rec.cost_sheet_hired_service_ids:
                total += line.cost_price_subtotal
            rec.amount_hired_service_cost = total            

    @api.depends('cost_sheet_material_ids', 'cost_sheet_labour_ids', 'cost_sheet_equipment_ids', 'cost_sheet_overhead_ids', 'cost_sheet_hired_service_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.amount_material_cost + rec.amount_labour_cost + rec.amount_equipment_cost + rec.amount_overhead_cost + rec.amount_hired_service_cost

    @api.depends('agriculture_cost_sheet_id')
    def _compute_lines(self):
        for rec in self:
            cost_sheet = rec.agriculture_cost_sheet_id

            # Vacío los campos:
            rec.crop_id = False
            rec.finca_id = False
            rec.project_id = False
            rec.planning_date = False

            # Vacío las líneas:
            rec.cost_sheet_material_ids = [(5, 0, 0)]
            rec.cost_sheet_labour_ids = [(5, 0, 0)]
            rec.cost_sheet_equipment_ids = [(5, 0, 0)]
            rec.cost_sheet_overhead_ids = [(5, 0, 0)]
            rec.cost_sheet_hired_service_ids = [(5, 0, 0)]    
                             
            if rec.agriculture_cost_sheet_id:
                rec.crop_id = cost_sheet.crop_id
                rec.finca_id = cost_sheet.finca_id
                rec.project_id = cost_sheet.project_id
                rec.planning_date = cost_sheet.planning_date

                materials = []
                labours = []
                equipments = []
                overheads = []
                hired_services = []     

                cost_sheet_lines = self.env['agriculture.cost.sheet.lines'].search([('agriculture_cost_sheet_id', '=', cost_sheet.id)])
                for line in cost_sheet_lines:
                    row = {
                        'internal_type': line.internal_type,
                        'job_type_id': line.job_type_id,
                        'product_id': line.product_id,
                        
                        # Labours:
                        'employee_id': line.employee_id,
                        
                        # Equipments:
                        'vehicle_id': line.vehicle_id,
                        
                        # Hired Services:
                        'partner_id': line.partner_id,

                        'quantity': line.quantity,
                        'qty_available': line.qty_available,                                                   
                        'finca_id': line.finca_id,
                        'task_id': line.task_id,
                        'parcel_id': line.parcel_id,
                        'tablon_id': line.tablon_id,
                        'hours': line.hours,
                        'cost_unit': line.cost_unit,
                        'cost_price_subtotal': line.cost_price_subtotal              
                    }
                    if line.internal_type == 'material':
                        materials.append((0, 0, row))
                    if line.internal_type == 'labour':
                        labours.append((0, 0, row))
                    if line.internal_type == 'equipment':
                        equipments.append((0, 0, row))
                    if line.internal_type == 'overhead':
                        overheads.append((0, 0, row))
                    if line.internal_type == 'hired_service':
                        hired_services.append((0, 0, row))                                                                            

                rec.cost_sheet_material_ids = materials
                rec.cost_sheet_labour_ids = labours
                rec.cost_sheet_equipment_ids = equipments
                rec.cost_sheet_overhead_ids = overheads
                rec.cost_sheet_hired_service_ids = hired_services

    def _inverse_lines(self):
        """ Little hack to make sure that when you change something on these objects, it gets saved"""
        pass

    @api.model
    def create(self, vals): 
        # workday_date = vals.get('workday_date')
        # row_count = self.env['agriculture.workday.spreadsheet'].search_count([
        #     ('workday_date', '=', workday_date),
        # ])
        # if row_count > 0:
        #     raise ValidationError(_('There is already a record with the indicated date'))
        # else:
        #     # vals['name'] = self.env['ir.sequence'].next_by_code('agriculture.workday.spreadsheet')
        #     workday_date = str(self.workday_date).replace('-', '/')
        #     vals['name'] = f'WORKDAY/{workday_date}'
        #     return super(AgricultureWorkdaySpreadsheet, self).create(vals)   
        # ===================================================================== #
        workday_date = str(vals.get('workday_date')).replace('-', '/')
        vals['name'] = f'WORKDAY/{workday_date}'
        
        return super(AgricultureWorkdaySpreadsheet, self).create(vals)         


    def write(self, vals): 
        # workday_date = vals.get('workday_date')
        # row_count = self.env['agriculture.workday.spreadsheet'].search_count([
        #     ('workday_date', '=', workday_date),
        # ])
        # if row_count > 0:
        #     raise ValidationError(_('There is already a record with the indicated date'))
        # else:
        #     # vals['name'] = self.env['ir.sequence'].next_by_code('agriculture.workday.spreadsheet')
        #     workday_date = str(self.workday_date).replace('-', '/')
        #     vals['name'] = f'WORKDAY/{workday_date}'
        #     return super(AgricultureWorkdaySpreadsheet, self).write(vals)   

        workday_date = str(self.workday_date).replace('-', '/')
        vals['name'] = f'WORKDAY/{workday_date}'
        vals['state'] = 'draft'
        return super(AgricultureWorkdaySpreadsheet, self).write(vals)          



    # @api.onchange('agriculture_cost_sheet_id')
    # def _onchange_agriculture_cost_sheet_id(self):
    #     if self.agriculture_cost_sheet_id:
    #         breakpoint()
    #         cost_sheet = self.env['agriculture.cost.sheet'].search([('id', '=', self.agriculture_cost_sheet_id.id)])
            
    #         self.crop_id = cost_sheet.crop_id
    #         self.finca_id = cost_sheet.finca_id
    #         self.project_id = cost_sheet.project_id
    #         self.planning_date = cost_sheet.planning_date

    #         materials = []
    #         labours = []
    #         equipments = []
    #         overheads = []
    #         hired_services = []

    #         cost_sheet_lines = self.env['agriculture.cost.sheet.lines'].search([('agriculture_cost_sheet_id', '=', self.agriculture_cost_sheet_id.id)])
    #         for line in cost_sheet_lines:
    #             row = {
    #                 'internal_type': line.internal_type,
    #                 'job_type_id': line.job_type_id,
    #                 'product_id': line.product_id,
                    
    #                 # Labours:
    #                 'employee_id': line.employee_id,
                    
    #                 # Equipments:
    #                 'vehicle_id': line.vehicle_id,
                    
    #                 # Hired Services:
    #                 'partner_id': line.partner_id,

    #                 'quantity': line.quantity,
    #                 'qty_available': line.qty_available,                                                   
    #                 'finca_id': line.finca_id,
    #                 'task_id': line.task_id,
    #                 'parcel_id': line.parcel_id,
    #                 'tablon_id': line.tablon_id,
    #                 'hours': line.hours,
    #                 'cost_unit': line.cost_unit,
    #                 'cost_price_subtotal': line.cost_price_subtotal              
    #             }
    #             if line.internal_type == 'material':
    #                 materials.append((0, 0, row))
    #             if line.internal_type == 'labour':
    #                 labours.append((0, 0, row))
    #             if line.internal_type == 'equipment':
    #                 equipments.append((0, 0, row))
    #             if line.internal_type == 'overhead':
    #                 overheads.append((0, 0, row))
    #             if line.internal_type == 'hired_service':
    #                 hired_services.append((0, 0, row))                                                                            

    #         # Vacío las líneas:
    #         self.cost_sheet_material_ids = [(5, 0, 0)]
    #         self.cost_sheet_labour_ids = [(5, 0, 0)]
            
    #         # raise UserError(_(f'materials: {materials}'))
    #         self.cost_sheet_material_ids = materials
    #         self.cost_sheet_labour_ids = labours
    #         self.cost_sheet_equipment_ids = equipments
    #         self.cost_sheet_overhead_ids = overheads
    #         self.cost_sheet_hired_service_ids = hired_services

    #         breakpoint()           

class AgricultureWorkdaySpreadsheetLines(models.Model):
    _name = 'agriculture.workday.spreadsheet.lines'

    agriculture_workday_spreadsheet_id = fields.Many2one('agriculture.workday.spreadsheet', string='Workday Spreadsheet', required=False, tracking=True)

    # operation_type = fields.Selection(
    #     [
    #         ('internal_requisition', 'Internal Requisition'),
    #         ('purchase', 'Purchase')
    #     ],
    #     string='Operation Type',
    #     # required=True,
    #     readonly=True,
    #     tracking=True,
    #     compute='_compute_operation_type',
    #     store=True
    # )    

    internal_type = fields.Selection(
        [
            ('material', 'Material'),
            ('labour', 'Labour'),
            ('equipment', 'Equipment'),
            ('overhead', 'Overhead'),
            ('hired_service', 'Hired Service')
        ],
        string='Internal Type',
        tracking=True, 
    )    

    date = fields.Date(string='Date', tracking=True)
    job_type_id = fields.Many2one('job.type', string='Job Type', tracking=True)
    product_id = fields.Many2one('product.product', string='Product', tracking=True)
    # Only for Equipments:
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    # Only for Labours:
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    description = fields.Char(string='Description', tracking=True)
    reference = fields.Char(string='Reference', tracking=True)
    
    # ============================================================ #
    finca_id = fields.Many2one(
        'agriculture.fincas',
        string='Farm',
        readonly=True,
        tracking=True
    )     

    task_id = fields.Many2one(
        'project.task',
        required=True,
        string='Activity',
        tracking=True,
    )         

    parcel_id = fields.Many2one(
        'agriculture.parcelas',
        string='Parcel',
        required=True,
        tracking=True
    )         

    tablon_id = fields.Many2one(
        'agriculture.tablon',
        string='Plank',
        tracking=True
    )                   
    # ============================================================ #     
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        tracking=True
    )    

    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        tracking=True
    )
    
    quantity = fields.Float(
        string='Quantity',
        tracking=True,
        default=1
    )

    qty_available = fields.Float(
        string='On Hand',
        related=('product_id.qty_available'),
        readonly=True,
        tracking=True
    )    

    hours = fields.Float(string='Hours', tracking=True)
    cost_unit = fields.Float(string='Cost / Unit', tracking=True)
    hectares_worked = fields.Float(string='Hectares Worked', tracking=True)
    actual_timesheet_hours = fields.Float(string='Actual Timesheet Hours', tracking=True)
    
    cost_price_subtotal = fields.Float(
        string='Cost Price Sub Total', 
        tracking=True, 
        compute='_compute_cost_price_subtotal', 
        store=True
    )
    
    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity:
            if self.quantity <= 0:
                raise ValidationError(_('Quantity cannot be less than or equal to 0.'))
            return True           

    @api.depends('quantity', 'cost_unit')
    def _compute_cost_price_subtotal(self):
        for line in self:
            cost_price_subtotal = 0
            if line.quantity:
                cost_price_subtotal = line.quantity * line.cost_unit
            else:
                cost_price_subtotal = line.cost_unit
            line.update({
                'cost_price_subtotal': cost_price_subtotal
            })    
    