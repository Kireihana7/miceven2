# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class CropMaterialManagement(models.Model):
    _name = 'crop.material.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    @api.model
    def default_get(self, fields):
        res = super(CropMaterialManagement, self).default_get(fields)
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
        string='Description',
        tracking=True
    )       

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

    description = fields.Text(string='Description', tracking=True)

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

    crop_material_ids = fields.One2many('crop.material.management.lines', 'crop_material_id', 'Crop Materials', copy=True, auto_join=True, tracking=True)
    # ============================================================ #
    @api.depends('crop_material_ids')
    def _compute_total_pay_amount(self):
        for rec in self:
            total = 0
            for line in rec.crop_material_ids:
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
    @api.constrains('crop_material_ids')
    def _check_crop_material_ids(self):
        if not self.crop_material_ids:
            raise ValidationError(_('Add at least one crop material.'))

    # ============================================================ #
    @api.constrains('total_pay_amount')
    def _check_total_pay_amount(self):
        for rec in self:
            if rec.total_pay_amount <= 0:
                raise ValidationError(_('The Total Pay Amount must not be less or equal to 0.00.'))            
 
    @api.model    
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('crop.material.management') or _('New')        
        res = super(CropMaterialManagement, self).create(vals)

        # Verificando si se usó la plantilla de tareas o no:    
        usar_tareas = self.env.context.get('default_usar_tareas')

        id_field_name = 'farmer_request_id'
        id_value = vals.get('farmer_request_id')
        if usar_tareas == True:
            id_field_name = 'task_id'
            id_value = vals.get('task_id')             

        # Último ID del modelo 'crop.material.management':
        last_crop_material_obj = self.env['crop.material.management'].search([])[-1]
        crop_material_id = last_crop_material_obj.id
        crop_project_template_id = last_crop_material_obj.crop_project_template_id.id

        # Insertando datos:
        self.env['crop.request.transaction'].create({
            id_field_name: id_value,
            'crop_material_id': crop_material_id,
            'crop_project_template_id': crop_project_template_id,
            'type': 'crop_material_management'
        })        
        
        return res      

class CropMaterialManagementLines(models.Model):
    _name = 'crop.material.management.lines'
    _rec_name = 'product_id'
    
    crop_material_id = fields.Many2one(
        'crop.material.management',
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
            ('product_tmpl_id.type', '=', 'product'),
            ('product_tmpl_id.equipo_agricola', '=', False), 
            ('product_tmpl_id.maintenance_ok', '=', False),
            ('product_tmpl_id.maintenance_as_product', '=', False),
            ('product_tmpl_id.mano_de_obra', '=', False)
        ],
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
    
    price = fields.Float(string='Price', tracking=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount', store=True, tracking=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.price = self.product_id.list_price

    @api.depends('quantity', 'price')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = rec.price * rec.quantity          