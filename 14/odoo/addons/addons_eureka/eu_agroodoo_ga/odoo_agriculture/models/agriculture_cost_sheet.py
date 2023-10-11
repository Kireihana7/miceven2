# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _  
from odoo.exceptions import UserError, ValidationError, Warning

class AgricultureCostSheet(models.Model):
    _name = 'agriculture.cost.sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(
        string='Name',
        default='New',
        required=True,
        tracking=True
    )

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

    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    
    purchase_id = fields.Many2one('purchase.order', readonly=True, string='Purchase Order', tracking=True)
    purchase_order_count = fields.Integer('Purchase Order Count', compute='_compute_purchase_order_count', store=True, tracking=True)

    agriculture_workday_spreadsheet_id = fields.Many2one('agriculture.workday.spreadsheet', string='Workday Planning', required=False, tracking=True)
    # agriculture_workday_spreadsheet_count = fields.Integer('Workday Spreadsheet Count', compute='_compute_agriculture_workday_spreadsheet_count', store=True, tracking=True)    
    
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Pedido interno',
        readonly=True,
        copy=False,
        tracking=True
    )    
    count_rq = fields.Integer("Internal Requisition", compute='_compute_rq_count', store=True, tracking=True)

    cost_sheet_material_ids = fields.One2many(
        'agriculture.cost.sheet.lines',
        'agriculture_cost_sheet_id',
        string='Materials',
        domain=[('internal_type', '=', 'material')],
        copy=True, 
        auto_join=True,
        tracking=True
    )        

    cost_sheet_labour_ids = fields.One2many(
        'agriculture.cost.sheet.lines',
        'agriculture_cost_sheet_id',
        string='Labours',
        domain=[('internal_type', '=', 'labour')],
        copy=True, 
        auto_join=True,
        tracking=True
    )       

    cost_sheet_equipment_ids = fields.One2many(
        'agriculture.cost.sheet.lines',
        'agriculture_cost_sheet_id',
        string='Equipments',
        domain=[('internal_type', '=', 'equipment')],
        copy=True, 
        auto_join=True,
        tracking=True
    )            

    cost_sheet_overhead_ids = fields.One2many(
        'agriculture.cost.sheet.lines',
        'agriculture_cost_sheet_id',
        string='Overheads',
        domain=[('internal_type', '=', 'overhead')],
        copy=True, 
        auto_join=True,
        tracking=True
    )    

    cost_sheet_hired_service_ids = fields.One2many(
        'agriculture.cost.sheet.lines',
        'agriculture_cost_sheet_id',
        string='Hired Services',
        domain=[('internal_type', '=', 'hired_service')],
        copy=True, 
        auto_join=True,
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
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled'),
            ('processed', 'Processed'),
        ],
        string="State",
        default='new',
        # required=True,
        tracking=True
    )

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})        

    def action_set_to_draft(self):
        self.write({'state': 'draft'})            

    # ======================== Inventory Requisition ======================== #
    def _get_location_id(self):
        domain =[('id', '=', -1)]
        employee_list=[]
        some_model = self.env['stock.location'].sudo().search([])
        for each in some_model:
            contador = 0
            for tabulador in each.complete_name:
                slash = "/"
                if tabulador in slash:
                    contador = contador + 1
            if contador < 2: 
                employee_list.append(each.id)
        if employee_list:
            domain =[('id', 'in', employee_list),('usage','in',('internal','supplier'))]
            return domain
        return domain

    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de origen',
        domain =_get_location_id,
        copy=True,
        tracking=True
    )    

    dest_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de Destino',
        domain ="[('usage','!=','view')]",
        required=False,
        copy=True,
        tracking=True
    )

    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Tipo de operación',
        domain="['|',('code','=','internal'),('code','=','outgoing'),('company_id', '=',company_id)]",
        copy=False,
        tracking=True
    )            

    # @api.model
    @api.depends('purchase_id')
    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = self.env['purchase.order'].search_count([('agriculture_cost_sheet_id', '=', rec.id)])

    # @api.model
    # @api.depends('agriculture_workday_spreadsheet_id')
    # def _compute_agriculture_workday_spreadsheet_count(self):
    #     for rec in self:
    #         if rec.agriculture_workday_spreadsheet_id:
    #             rec.agriculture_workday_spreadsheet_count = 1
    #         else:
    #             # rec.agriculture_workday_spreadsheet_count = self.env['agriculture.workday.spreadsheet'].search_count([('agriculture_cost_sheet_id', '=', rec.id)])
    #             rec.agriculture_workday_spreadsheet_count = 0

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

    def get_analytic_accounts(self):
        return True

    def action_process_costs(self):
        # Se procesa la planificación:
        self.write({'state': 'processed'})

        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']       

        for rec in self:
            # Internal Requisition:
            cost_sheet_lines = self.env['agriculture.cost.sheet.lines'].search([('agriculture_cost_sheet_id', '=', rec.id)])
            
            stock_picking_products = 0
            purchase_products = 0
            
            for line in cost_sheet_lines:
                # Internal Requisition:
                if line.operation_type == 'internal_requisition':   
                    stock_picking_products += 1

                # Purchase:
                if line.operation_type == 'purchase':   
                    purchase_products += 1                    

            if stock_picking_products > 0:
                if not rec.location_id.id:
                    raise Warning(_('Seleccione la ubicación de origen del detalle de pedido.'))
                if not rec.custom_picking_type_id.id:
                    raise Warning(_('Seleccion el Tipo de salida debajo de los detalles.'))
                if not rec.dest_location_id:
                    raise Warning(_('Selecciona la ubicación de destino de los detalles de pedido.'))                

            # ============== Datos del Crop Request ============== #
            # division_terreno = rec.farmer_request_id.division_terreno

            if purchase_products > 0:
                # Purchase Order:
                purchase_order = self.env['purchase.order'].search([('agriculture_cost_sheet_id', '=', rec.id)])
                if len(purchase_order) == 0:
                    employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                    # Creating Purchase Order:
                    po_vals = {
                        # 'partner_id': partner.id,
                        'partner_id': employee_id.address_home_id.id,
                        'currency_id': rec.env.company.currency_id.id,
                        'date_order': fields.Date.today(),
                        'company_id': rec.company_id.id,
                        'agriculture_cost_sheet_id': rec.id,
                        'origin': rec.name,
                        # 'notes': rec.reason,
                    }
                    purchase_order = purchase_obj.create(po_vals)        
                    rec.write({
                        'purchase_id': purchase_order.id
                    })                

                    # 1 - Lines (Purchase):
                    for line in cost_sheet_lines:
                        # Purchase:
                        if line.operation_type == 'purchase':

                            # Finca:
                            # finca_obj = line.finca_id
                            finca_obj = rec.finca_id
                            finca_id = finca_obj.id

                            # Parcela:
                            parcel_obj = line.parcel_id
                            parcel_id = parcel_obj.id
                            
                            # Tablón:
                            tablon_obj = line.tablon_id
                            tablon_id = tablon_obj.id        

                            # =============== Actividad =============== #
                            task_obj = line.task_id
                            task_id = task_obj.id
                            task_name = f'{rec.name} / {task_obj.name}'
                            # task_name = f'[{farm_name}] -> {task_id.name}'

                            activity_analytic_account_obj = self.env['account.analytic.account'].search([
                                ('finca_id', '=', finca_id),
                                ('task_id', '=', task_id)
                            ])
                            if len(activity_analytic_account_obj) == 0:
                                # Creando Centro de Costo para la actitivad / tarea (su C.C padre será la finca seleccionada):
                                activity_analytic_account_obj = self.env['account.analytic.account'].create({
                                    'name': task_name,
                                    'parent_id': finca_obj.analytic_account_id.id,
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
                            
                            # parcel_analytic_account_obj = self.env['account.analytic.account'].search([
                            #     ('finca_id', '=', finca_id),
                            #     ('parcel_id', '=', parcel_id),
                            #     ('type', '=', 'parcel')
                            # ])
                            # # Agregando Actividad al Many2many de Actividades de la Parcela:
                            # parcel_analytic_account_obj.write({
                            #     'task_ids': [
                            #         (4, task_id, 0)
                            #     ]                                     
                            # })               

                            analytic_account_id_1 = finca_obj.analytic_account_id.id
                            analytic_account_id_2 = activity_analytic_account_obj.id
                            analytic_account_id_3 = False
                            analytic_account_id_4 = False

                            # Determinando la División del Terreno:
                            # =============== Parcela o Tablón =============== #                    
                            # if division_terreno == 'parcel':
                            #     analytic_account_id_3 = parcel_analytic_account_obj.id
                            # if division_terreno == 'plank':
                            #     analytic_account_id_3 = parcel_analytic_account_obj.id

                            if parcel_obj: # Parcela
                                analytic_account_id_3 = parcel_obj.analytic_account_id.id
                            if tablon_obj: # Tablón
                                analytic_account_id_3 = parcel_obj.analytic_account_id.id

                                # Analytic Account for Plank:
                                # tablon_analytic_account_obj = self.env['account.analytic.account'].search([
                                #     ('finca_id', '=', finca_id),
                                #     ('parcel_id', '=', parcel_id),
                                #     ('tablon_id', '=', tablon_id),
                                #     ('type', '=', 'plank')
                                # ])                        
                                # analytic_account_id_4 = tablon_analytic_account_obj.id
                                analytic_account_id_4 = tablon_obj.analytic_account_id.id

                            if line.quantity == False or line.quantity == 0:
                                line.quantity = 1

                            po_line_vals = {
                                'product_id': line.product_id.id,
                                'name':line.product_id.name,
                                # 'product_qty': line.qty,
                                'product_qty': line.quantity,
                                # 'product_uom': line.uom.id,
                                'product_uom': line.uom_id.id,
                                'date_planned': fields.Date.today(),
                                # 'price_unit': line.product_id.standard_price,
                                'price_unit': line.cost_unit,
                                'order_id': purchase_order.id,
                                # 'analytic_account_id': self.analytic_account_id.id if self.analytic_use == 'header' else line.analytic_account_id.id,
                                'analytic_account_id_1': analytic_account_id_1,
                                'analytic_account_id_2': analytic_account_id_2,
                                'analytic_account_id_3': analytic_account_id_3,
                                'analytic_account_id_4': analytic_account_id_4,
                                'task_id': task_id,                            
                                'custom_cost_sheet_line_id': line.id
                                # 'custom_requisition_line_id': line.id
                            }                    
                            purchase_line_obj.sudo().create(po_line_vals)

            # ============================================================ #

            # 2 - Lines (Internal Requisition):
            stock_id = False
            if stock_picking_products > 0:
                # Creating Stock Picking:
                employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                # raise UserError(_(employee_id))
                picking_vals = {
                    # 'partner_id' : rec.employee_id.address_home_id.id,
                    'partner_id': employee_id.address_home_id.id,
                    #'min_date': fields.Date.today(),
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                    'picking_type_id': rec.custom_picking_type_id.id,#internal_obj.id,
                    # 'note': rec.reason,
                    # 'custom_requisition_id': rec.id,
                    'agriculture_cost_sheet_id': rec.id,
                    'origin': rec.name,
                    'company_id': rec.company_id.id,                        
                }
                stock_id = stock_obj.sudo().create(picking_vals)
                delivery_vals = {
                    'delivery_picking_id' : stock_id.id,
                }
                rec.write(delivery_vals)

                for line in cost_sheet_lines:
                    # Internal Requisition:
                    if line.operation_type == 'internal_requisition':   
                        pick_vals = rec._prepare_pick_vals(line, stock_id)
                        move_id = move_obj.sudo().create(pick_vals)

    
    def action_create_workday_spreadsheet(self):
        workday_date = str(fields.Date.today()).replace('-', '/')
        workday_date = f'WORKDAY/{workday_date}'
        workday_spreadsheet = self.env['agriculture.workday.spreadsheet'].create({
            'name': workday_date,
            'agriculture_cost_sheet_id': self.id,
            'project_id': self.project_id.id,
            'crop_id': self.crop_id.id,
            'finca_id': self.finca_id.id,
            'planning_date': self.planning_date,
            'workday_date': fields.Date.today()
        })

        agriculture_workday_spreadsheet_id = workday_spreadsheet.id
        
        self.write({
            'agriculture_workday_spreadsheet_id': agriculture_workday_spreadsheet_id
        })

        # Materials
        for line in self.cost_sheet_material_ids:
            self.env['agriculture.workday.spreadsheet.lines'].create({
                'agriculture_workday_spreadsheet_id': agriculture_workday_spreadsheet_id,
                'internal_type': line.internal_type,
                # 'operation_type': line.operation_type,
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'qty_available': line.qty_available,                                                   
                'finca_id': line.finca_id.id,
                'task_id': line.task_id.id,
                'parcel_id': line.parcel_id.id,
                'tablon_id': line.tablon_id.id,
                'hours': line.hours,
                'cost_unit': line.cost_unit,
                'cost_price_subtotal': line.cost_price_subtotal              
            }) 
        
        # Labours
        for line in self.cost_sheet_labour_ids:
            self.env['agriculture.workday.spreadsheet.lines'].create({
                'agriculture_workday_spreadsheet_id': agriculture_workday_spreadsheet_id,
                'internal_type': line.internal_type,
                # 'operation_type': line.operation_type,
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'employee_id': line.employee_id.id,                                            
                'finca_id': line.finca_id.id,
                'task_id': line.task_id.id,
                'parcel_id': line.parcel_id.id,
                'tablon_id': line.tablon_id.id,
                'hours': line.hours,
                'cost_unit': line.cost_unit,
                'cost_price_subtotal': line.cost_price_subtotal              
            })

        # Equipments
        for line in self.cost_sheet_equipment_ids:
            self.env['agriculture.workday.spreadsheet.lines'].create({
                'agriculture_workday_spreadsheet_id': agriculture_workday_spreadsheet_id,
                'internal_type': line.internal_type,
                # 'operation_type': line.operation_type,
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'vehicle_id': line.vehicle_id.id,                                            
                'finca_id': line.finca_id.id,
                'task_id': line.task_id.id,
                'parcel_id': line.parcel_id.id,
                'tablon_id': line.tablon_id.id,
                'hours': line.hours,
                'cost_unit': line.cost_unit,
                'cost_price_subtotal': line.cost_price_subtotal              
            }) 

        # Overheads
        for line in self.cost_sheet_overhead_ids:
            self.env['agriculture.workday.spreadsheet.lines'].create({
                'agriculture_workday_spreadsheet_id': agriculture_workday_spreadsheet_id,
                'internal_type': line.internal_type,
                # 'operation_type': line.operation_type,
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,                                 
                'finca_id': line.finca_id.id,
                'task_id': line.task_id.id,
                'parcel_id': line.parcel_id.id,
                'tablon_id': line.tablon_id.id,
                'hours': line.hours,
                'cost_unit': line.cost_unit,
                'cost_price_subtotal': line.cost_price_subtotal              
            })     

        # Hired Services
        for line in self.cost_sheet_hired_service_ids:
            self.env['agriculture.workday.spreadsheet.lines'].create({
                'agriculture_workday_spreadsheet_id': agriculture_workday_spreadsheet_id,
                'internal_type': line.internal_type,
                # 'operation_type': line.operation_type,
                'job_type_id': line.job_type_id.id,
                'product_id': line.product_id.id,
                'partner_id': line.partner_id.id,                                       
                'finca_id': line.finca_id.id,
                'task_id': line.task_id.id,
                'parcel_id': line.parcel_id.id,
                'tablon_id': line.tablon_id.id,
                'hours': line.hours,
                'cost_unit': line.cost_unit,
                'cost_price_subtotal': line.cost_price_subtotal              
            })                                                
            
    # @api.model
    @api.depends('delivery_picking_id')
    def _compute_rq_count(self):
        for rec in self:
            rec.count_rq = self.env['stock.picking'].sudo().search_count([('agriculture_cost_sheet_id', '=', rec.id)])

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

    @api.model
    def create(self, vals): 
        # planning_date = vals.get('planning_date')
        # row_count = self.env['agriculture.cost.sheet'].search_count([
        #     ('planning_date', '=', planning_date),
        # ])
        # if row_count > 0:
        #     raise ValidationError(_('There is already a record with the indicated date'))
        # else:
        #     # vals['name'] = self.env['ir.sequence'].next_by_code('agriculture.cost.sheet')
        #     planning_date = str(self.planning_date).replace('-', '/')
        #     vals['name'] = f'PLANNING/{planning_date}'
        #     return super(AgricultureCostSheet, self).create(vals)     

        # vals['name'] = self.env['ir.sequence'].next_by_code('agriculture.cost.sheet')}
        planning_date = str(vals.get('planning_date')).replace('-', '/')
        vals['name'] = f'PLANNING/{planning_date}'
        vals['state'] = 'draft'
        return super(AgricultureCostSheet, self).create(vals)             


    def write(self, vals): 
        # vals['name'] = self.env['ir.sequence'].next_by_code('agriculture.cost.sheet')
        planning_date = str(self.planning_date).replace('-', '/')
        vals['name'] = f'PLANNING/{planning_date}'
        return super(AgricultureCostSheet, self).write(vals)         

    def view_purchase_order(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('agriculture_cost_sheet_id', '=', self.id)]  
        action['context'] = {
            'default_agriculture_cost_sheet_id': self.id,
        }              
        return action   

    def show_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('agriculture_cost_sheet_id', '=', self.id)]  
        action['context'] = {
            'default_agriculture_cost_sheet_id': self.id,
        }              
        return action        
        # for rec in self:
        #     res = self.env.ref('stock.action_picking_tree_all')
        #     res = res.read()[0]
        #     res['domain'] = str([('agriculture_cost_sheet_id', '=', rec.id)])
        # return res        

    def view_workday_spreadsheet(self):
        action = self.env.ref('odoo_agriculture.action_agriculture_workday_spreadsheet').read()[0]
        action['domain'] = [('agriculture_cost_sheet_id', '=', self.id)]  
        action['context'] = {
            'default_agriculture_cost_sheet_id': self.id,
        }              
        return action   

    @api.onchange('crop_id')
    def _onchange_crop_id(self):
        self.project_id = self.env['project.project'].search([('project_template', '=', True), ('crop_id', '=', self.crop_id.id)])

    @api.onchange('finca_id')
    def _onchange_finca_id(self):
        if not self.finca_id:
            # self.cost_sheet_material_ids.finca_id = [(5, 0, 0)]
            self.cost_sheet_material_ids.parcel_id = [(5, 0, 0)]
            self.cost_sheet_material_ids.tablon_id = [(5, 0, 0)]
                            
class AgricultureCostSheetLines(models.Model):
    _name = 'agriculture.cost.sheet.lines'

    agriculture_cost_sheet_id = fields.Many2one('agriculture.cost.sheet', string='Workday Planning', required=False, tracking=True)

    operation_type = fields.Selection(
        [
            ('internal_requisition', 'Internal Requisition'),
            ('purchase', 'Purchase')
        ],
        string='Operation Type',
        # required=True,
        readonly=True,
        tracking=True,
        compute='_compute_operation_type',
        store=True
    )    

    internal_type = fields.Selection(
        [
            ('material', 'Material'),
            ('labour', 'Labour'),
            ('equipment', 'Equipment'),
            ('overhead', 'Overhead'),
            ('hired_service', 'Hired Service')
        ],
        string='Internal Type',
        required=True,
        tracking=True, 
    )    

    date = fields.Date(string='Date', tracking=True)
    job_type_id = fields.Many2one('job.type', string='Job Type', required=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, tracking=True)
    # Only for Equipments:
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    # Only for Labours:
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    description = fields.Char(string='Description', tracking=True)
    reference = fields.Char(string='Reference', tracking=True)
    
    # ============================================================ #
    finca_id = fields.Many2one(
        'agriculture.fincas',
        # required=True,
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
        # required=True,
        tracking=True
    )    

    uom_id = fields.Many2one(
        'uom.uom',
        related='product_id.uom_id',
        string='Unit of Measure',
        # required=True,
        tracking=True
    )
    
    quantity = fields.Float(
        string='Quantity',
        required=True,
        tracking=True,
        default=1
    )

    qty_available = fields.Float(
        string='On Hand',
        related=('product_id.qty_available'),
        readonly=True,
        required=True,
        tracking=True
    )    

    work_uom = fields.Selection(
        [
            ('by_hour', 'By Hours'),
            ('by_hectares', 'By Hectares')
        ],
        string='Work Unit of Measure',
        tracking=True, 
    )
    hours = fields.Float(string='Hours', tracking=True)
    hectares_worked = fields.Float(string='Hectares Worked', tracking=True)
    # cost_unit = fields.Float(string='Cost / Unit', compute='_compute_cost_unit', inverse='_inverse_cost_unit', tracking=True)
    cost_unit = fields.Float(string='Cost / Unit', tracking=True)

    actual_timesheet_hours = fields.Float(string='Actual Timesheet Hours', tracking=True)
    cost_price_subtotal = fields.Float(string='Cost Price Sub Total', tracking=True, compute='_compute_cost_price_subtotal', store=True)
    
    @api.onchange('quantity')
    def _onchange_quantity(self):
        if not self.quantity:
            return True
        else:
            if self.quantity <= 0:
                raise ValidationError(_('Quantity cannot be less than or equal to 0.'))

    @api.depends('quantity', 'qty_available')
    def _compute_operation_type(self):
        for line in self:
            operation_type = ''
            if line.internal_type == 'material':
                if line.quantity > line.qty_available:
                    operation_type = 'purchase'
                else:
                    operation_type = 'internal_requisition'
            else:
                operation_type = 'purchase'
            line.update({
                'operation_type': operation_type
            })    

    # @api.onchange('vehicle_id')
    # def _onchange_vehicle_id(self):
    #     if self.vehicle_id:
    #         # Datos del Horómetro:
    #         fleet_vehicle_hourmeter = self.env['fleet.vehicle.hourmeter'].search([('vehicle_id', '=', self.vehicle_id.id)])
    #         if len(fleet_vehicle_hourmeter) == 0:
    #             self.cost_unit = 0
    #         elif len(fleet_vehicle_hourmeter) == 1:
    #             self.cost_unit = fleet_vehicle_hourmeter[0].value
    #         elif len(fleet_vehicle_hourmeter) > 1:
    #             last_index = len(fleet_vehicle_hourmeter) - 1
    #             self.cost_unit = fleet_vehicle_hourmeter[last_index].value

    # @api.onchange('employee_id')
    # def _onchange_employee_id(self):
    #     if self.employee_id:
    #         # Consultando el salario del contrato del empleado seleccionado:
    #         hr_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
    #         if len(hr_contract) == 0:
    #             self.cost_unit = 0
    #         elif len(hr_contract) == 1:
    #             self.cost_unit = hr_contract[0].wage / 30
    #         elif len(hr_contract) > 1:
    #             last_index = len(hr_contract) - 1
    #             self.cost_unit = hr_contract[last_index].wage / 30

    @api.depends('employee_id', 'vehicle_id')
    def _compute_cost_unit(self):
        for rec in self:
            if rec.employee_id:
                # Consultando el salario del contrato del empleado seleccionado:
                hr_contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)])
                if len(hr_contract) == 0:
                    rec.cost_unit = 0
                elif len(hr_contract) == 1:
                    rec.cost_unit = hr_contract[0].wage / 30
                elif len(hr_contract) > 1:
                    last_index = len(hr_contract) - 1
                    rec.cost_unit = hr_contract[last_index].wage / 30           

            if rec.vehicle_id:
            # Datos del Horómetro:
                fleet_vehicle_hourmeter = self.env['fleet.vehicle.hourmeter'].search([('vehicle_id', '=', rec.vehicle_id.id)])
                if len(fleet_vehicle_hourmeter) == 0:
                    rec.cost_unit = 0
                elif len(fleet_vehicle_hourmeter) == 1:
                    rec.cost_unit = fleet_vehicle_hourmeter[0].value
                elif len(fleet_vehicle_hourmeter) > 1:
                    last_index = len(fleet_vehicle_hourmeter) - 1
                    rec.cost_unit = fleet_vehicle_hourmeter[last_index].value                

    def _inverse_cost_unit(self):
        pass

    @api.depends('quantity', 'cost_unit', 'hours')
    def _compute_cost_price_subtotal(self):
        for line in self:
            cost_price_subtotal = 0

            # Equipments (vehicle_id)
            if line.vehicle_id:
                # raise UserError('Hay "vehicle_id"')
                cost_price_subtotal = line.hours * line.cost_unit

            # Overheads and Hired Services:
            if line.quantity:
                cost_price_subtotal = line.quantity * line.cost_unit
            
            # Employee:
            if line.employee_id:
                cost_price_subtotal = line.cost_unit


            line.cost_price_subtotal = cost_price_subtotal
            # line.update({
            #     'cost_price_subtotal': cost_price_subtotal
            # })    
