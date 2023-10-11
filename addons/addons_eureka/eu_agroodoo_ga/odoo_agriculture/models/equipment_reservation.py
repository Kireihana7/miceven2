# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class EquipmentReservation(models.Model):
    _name = 'equipment.reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    @api.model
    def default_get(self, fields):
        res = super(EquipmentReservation, self).default_get(fields)
        res['task_id'] = self.env.context.get('default_task_id')
        res['farmer_request_id'] = self.env.context.get('default_farmer_request_id')
        res['crop_project_template_id'] = self.env.context.get('default_crop_project_template_id')
        return res

    number = fields.Char(
        string='Number',
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )

    name = fields.Char(
        string='Name',
        tracking=True
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

    reservation_type_use = fields.Selection(
        string='Reservation Type to use', 
        selection=[
            ('header', 'Por único seleccionado'),
            ('line', 'Por líneas')
        ],
        required=True,
        tracking=True
    )

    reservation_type = fields.Selection(string='Reservation Type', 
        selection=[
            ('own', 'Own'),
            ('rented', 'Rented'),
        ], tracking=True)    

    reservation_time_type_use = fields.Selection([
        ('header', 'Por único seleccionado'),
        ('line', 'Por líneas')],
        string='Reservation Time to use', 
        required=True,
        tracking=True
    )    
    
    reservation_time = fields.Selection(string='Reservation Type by Time', 
        selection=[
            ('hours', 'Hours'),
            ('days', 'Days'),
        ], tracking=True)    

    partner_id_type_use = fields.Selection([
        ('header', 'Por único seleccionado'),
        ('line', 'Por líneas')],
        string='Reservation Time to use', 
        required=False,
        tracking=True
    )    

    partner_id = fields.Many2one('res.partner',
        string='Vendor',
        tracking=True)    

    start_date = fields.Datetime(
        string='Start Date',
        tracking=True
        # required=True
    )

    end_date = fields.Datetime(
        string='End Date',
        tracking=True
        # required=True
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
        default='draft',)    

    total_pay_amount = fields.Float(string='Total Pay Amount', compute='_compute_total_pay_amount', store=True, tracking=True)

    equipment_reservation_ids = fields.One2many('equipment.reservation.lines', 'equipment_reservation_id', 'Equipments', copy=True, auto_join=True, tracking=True)

    @api.depends('equipment_reservation_ids')
    def _compute_total_pay_amount(self):
        for rec in self:
            total = 0
            for line in rec.equipment_reservation_ids:
                total = total + line.price_subtotal
            rec.total_pay_amount = total            

    def action_request(self):
        self.state = 'requested'

    def action_approve(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.state = 'draft'        

    # ============================================================ #
    
    @api.onchange('reservation_type_use')
    def _onchange_reservation_type_use(self):
        if self.reservation_type_use != 'header':
            self.reservation_type = ''    
            self.partner_id = ''    
            for line in self.equipment_reservation_ids:
                line.reservation_type_line = ''
                line.partner_id = False    

    @api.onchange('reservation_type')
    def _onchange_reservation_type(self):
        if self.equipment_reservation_ids:
            for line in self.equipment_reservation_ids:
                line.reservation_type_line = self.reservation_type
                line.partner_id = self.partner_id  
                 
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.equipment_reservation_ids:
            for line in self.equipment_reservation_ids:
                line.partner_id = self.partner_id  

    # ============================================================ #        

    @api.onchange('reservation_time_type_use')
    def _onchange_reservation_time_type_use(self):
        if self.reservation_type_use != 'header':
            self.reservation_time = ''            
            for line in self.equipment_reservation_ids:
                line.reservation_time_line = ''

    @api.onchange('reservation_time')
    def _onchange_reservation_time(self):
        if self.equipment_reservation_ids:
            for line in self.equipment_reservation_ids:
                line.reservation_time_line = self.reservation_time       
    
    # ============================================================ #

    @api.constrains('equipment_reservation_ids')
    def _check_equipment_reservation_ids(self):
        if not self.equipment_reservation_ids:
            raise ValidationError(_('Add at least one equipment line.'))        

    # ============================================================ #
    @api.constrains('total_pay_amount')
    def _check_total_pay_amount(self):
        for rec in self:
            if rec.total_pay_amount <= 0:
                raise ValidationError(_('The Total Pay Amount must not be less or equal to 0.00.'))            
 
    @api.model    
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('equipment.reservation') or _('New')        
        res = super(EquipmentReservation, self).create(vals)

        # Verificando si se usó la plantilla de tareas o no:    
        usar_tareas = self.env.context.get('default_usar_tareas')
        # raise UserError(_(f'usar_tareas: {usar_tareas}'))
        # raise UserError(_(f'farmer_request_id: {vals.get("farmer_request_id")}'))

        id_field_name = 'farmer_request_id'
        id_value = vals.get('farmer_request_id')
        if usar_tareas == True:
            id_field_name = 'task_id'
            id_value = vals.get('task_id')        

        # Último ID del modelo 'equipment.reservation':
        last_equipment_reservation_obj = self.env['equipment.reservation'].search([])[-1]
        equipment_reservation_id = last_equipment_reservation_obj.id
        crop_project_template_id = last_equipment_reservation_obj.crop_project_template_id.id

        # Insertando datos:
        self.env['crop.request.transaction'].create({
            id_field_name: id_value,
            'equipment_reservation_id': equipment_reservation_id,
            'crop_project_template_id': crop_project_template_id,
            'type': 'equipment_reservation'
        })        
        
        return res        

class EquipmentReservationLines(models.Model):
    _name = 'equipment.reservation.lines'
    _rec_name = 'product_id'
    
    equipment_reservation_id = fields.Many2one(
        'equipment.reservation',
        string='Equipment Reservation',
        ondelete='cascade',
        required=True,
        index=True,
        readonly=True,
        tracking=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[
            ('product_tmpl_id.is_agriculture','=', True), 
            ('product_tmpl_id.equipo_agricola', '=', True), 
            ('product_tmpl_id.maintenance_ok', '=', True)
        ],
        required=True,
        tracking=True
    )

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

    quantity = fields.Float(
        string='Quantity',
        required=True,
        tracking=True
    )    

    qty_available = fields.Float(
        string='On Hand',
        related=('product_id.qty_available'),
        readonly=True,
        required=True,
        tracking=True
    )

    reservation_type_line = fields.Selection(string='Reservation Type', 
        selection=[
            ('own', 'Own'),
            ('rented', 'Rented'),
        ], tracking=True)    

    reservation_time_line = fields.Selection(string='Reservation Type by Time', 
        selection=[
            ('hours', 'Hours'),
            ('days', 'Days'),
        ], tracking=True)            
    
    partner_id = fields.Many2one('res.partner',
        string='Vendor', tracking=True)    

    price = fields.Float(string='Price', tracking=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount', store=True, tracking=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.equipment_reservation_id.reservation_type_use == 'header':
            self.reservation_type_line = self.equipment_reservation_id.reservation_type
            self.reservation_time_line = self.equipment_reservation_id.reservation_time
            self.partner_id = self.equipment_reservation_id.partner_id.id

        self.price = self.product_id.list_price
    
    @api.depends('quantity', 'price')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = rec.price * rec.quantity    
    '''
    @api.onchange('quantity')
    def _onchange_quantity(self):
        for rec in self:
            rec.price = rec.price * rec.quantity    
    '''