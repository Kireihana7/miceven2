# -*- coding: utf-8 -*-

from dataclasses import field
from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import Warning, UserError

class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Requisición de Compra'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']      # odoo11
    _order = 'id desc'
    
    #@api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('0', '6', '7'):
                raise Warning(_('No puedes eliminar una Orden de Requisición que no esté en Borrador, Cancelada o Rechazada.'))
        return super(MaterialPurchaseRequisition, self).unlink()

    name = fields.Char(
        string='Número',
        index=True,
        readonly=1,
        default='Nuevo',tracking=True,
    )
    state = fields.Selection([ 
        ('0', 'Nuevas'), # 0 = draft
        ('1', 'Esperando Aprobación del Departamento'), # 1 = 1
        ('2', 'Esperando Aprobación del Gerente'), # 2 =2
        ('3', 'Aprobado'), # 3 = approve
        ('4', 'Requisición de Compra Creada'), # 4 = stock
        ('5', 'Finalizadas'), # 5 = receive
        ('6', 'Canceladas'), # 6 = cancel
        ('7', 'Rechazadas'),('8', 'Fusionada')], # 7 = reject
        default='0',
        readonly=1,
        track_visibility='onchange',
        string='Estatus',tracking=True,
    )
    request_date = fields.Date(
        string='Fecha de requisición',
        default = fields.Date.context_today,
        required=True,
        readonly=1,tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Departamento',
        default=lambda self: self.env.user.department_id,
        required=True,
        copy=True,
        readonly=1,tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Solicitante', 
        required=True, tracking=True,
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')],
        string='Prioridad', tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Creado por',
        default=lambda self: self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1),
        required=True,
        copy=True,tracking=True,
        readonly=1,
    )
    approve_manager_id = fields.Many2one(
        'hr.employee',
        string='Gerente del Departamento',
        readonly=True,
        copy=False,tracking=True,
    )
    reject_manager_id = fields.Many2one(
        'hr.employee',
        string='Rechazo del Gerente del Departamento:',
        readonly=True,tracking=True,
    )
    approve_employee_id = fields.Many2one(
        'hr.employee',
        string='Aprobado por',
        readonly=True,tracking=True,
        copy=False,
    )
    rq_create_for = fields.Many2one(
        'hr.employee',
        string='Requisición de compra creada por:',
        readonly=True,tracking=True,
        copy=False,
    )
    recieve_for = fields.Many2one(
        'hr.employee',
        string='Recibido por:',
        readonly=True,tracking=True,
        copy=False,
    )
    reject_employee_id = fields.Many2one(
        'hr.employee',
        string='Rechazado por',
        readonly=True,
        copy=False,tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,tracking=True,
        readonly=1,
    )
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

    def _get_location_id_get(self):
           return self.env['stock.location'].search(self._get_location_id()).filtered(lambda x:x.company_id==self.env.company or x.company_id==False)[:1]
            
    def _get_location_id_dest_get(self):

           return self.env['stock.location'].search([('usage','!=','view')],limit=1)
            
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de origen',
        domain =_get_location_id,
        default=_get_location_id_get,
        copy=True,tracking=True,
    )
    requisition_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        string='Línea de Solicitudes de Compra',
        copy=True,tracking=True
    )
    date_end = fields.Date(
        string='Fecha tope', 
        readonly=True,
        help='Fecha final para la que se necesita el producto',
        copy=True,tracking=True,
    )
    date_done = fields.Date(
        string='Fecha de finalización', 
        readonly=True, tracking=True,
        help='Fecha de la Finalización de la Requisición',
    )
    managerapp_date = fields.Date(
        string='Fecha de Aprobación del Departamento:',
        readonly=True,tracking=True,
        copy=False,
    )
    manareject_date = fields.Date(
        string='Fecha de rechazo del gerente del Departamento:',
        readonly=True,tracking=True,
    )
    userreject_date = fields.Date(
        string='Fecha de rechazo',
        readonly=True,tracking=True,
        copy=False,
    )
    userrapp_date = fields.Date(
        string='Fecha de aprobación:',
        readonly=True,tracking=True,
        copy=False,
    )
    rq_create_for_date = fields.Date(
        string='Fecha de creación de la Requisición de Compra:',
        readonly=True,tracking=True,
        copy=False,
    )
    recieve_for_date = fields.Date(
        string='Fecha de la recepción:',
        readonly=True,
        copy=False,tracking=True,
    )
    receive_date = fields.Date(
        string='Fecha estimada',
        default = fields.Date.context_today,
        required=True,
        readonly=True,tracking=True,
        copy=False,
    )
    reason = fields.Text(
        string='Motivo(s) de las requisición(es)',
        required=False,
        copy=True,tracking=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Centro de Costo',
        copy=True,tracking=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de Destino',
        domain ="[('usage','!=','view')]",
        required=False,
        default=_get_location_id_dest_get,
        copy=True,tracking=True,
    )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Pedido interno',
        readonly=True,tracking=True,
        copy=False,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsable de la requisición',
        copy=True,
        required=True,tracking=True,
        domain="[('requisition_super', '=', True),('company_id', '=', company_id)]"
    )
    employee_confirm_id = fields.Many2one(
        'hr.employee',
        string='Confirmado por',
        readonly=True,
        copy=False,tracking=True,
    )
    confirm_date = fields.Date(
        string='Fecha de confirmación',
        readonly=True,
        copy=False,tracking=True,
    )
    
    purchase_order_ids = fields.One2many(
        'purchase.order',
        'custom_requisition_id',
        string='Requisiciones de Compra',tracking=True,
    )
    purchase_agreement_ids = fields.One2many(
        'purchase.agreement',
        'custom_requisition_id',tracking=True,
        string='Requisiciones de Compra',
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Tipo de operación',
        copy=False,tracking=True,
        default=lambda self: self.env['stock.picking.type'].search(['|',('code','=','internal'),('code','=','outgoing'),('company_id', '=',self.env.company.id)],limit=1)
    )
        # domain="['|',('code','=','internal'),('code','=','outgoing'),('company_id', '=',company_id)]",

    count_rq = fields.Integer("Requisición Interna", compute='_compute_rq_count',tracking=True)
    # branch_id = fields.Many2one('res.branch', string="Branch", required=True)
    analytic_use = fields.Selection([
        ('header', 'Por único seleccionado'),
        ('line', 'Por líneas')],
        string='Centro de Costo a Utilizar', 
        required=True,tracking=True
    )
    is_departamento = fields.Boolean(string="Es Gerente de Departamento",compute="_compute_is_departamento",tracking=True)
    is_gerente = fields.Boolean(string="Es Gerente",compute="_compute_is_gerente",Tracking=True)
    is_responsable = fields.Boolean(string="Es Responsable",compute="_compute_is_responsable",Tracking=True)
    requisition_type=fields.Selection([('internal','Requisición Interna'),('tender','Licitación de Compra')],tracking=True,string='Tipo de Requisición',default='internal',required=True)
    fused_with_requisition_id=fields.Many2one('material.purchase.requisition','Requisicion fusionada',tracking=True)
    fused_with_licitation_id=fields.Many2one('purchase.agreement','Licitacion fusionada',tracking=True)
    product_category_id=fields.Many2one('product.category', string="Categoría de producto",tracking=True)
    
    #region METHODS
    # @api.constrains('requisition_line_ids')
    # def _constrain_requesition_lines(self):
    #     for rec in self:
    #         for line in rec.requisition_line_ids:
    #             if rec.product_category_id and line.product_id and line.categ_id!=rec.product_category_id:
    #                 raise UserError("Posee productos que no poseen la misma categoria que la orden")

    @api.onchange('analytic_use')
    def _onchange_analytic_use(self):
        for rec in self:
            if rec.analytic_use=='line':
                rec.analytic_account_id=False
    @api.depends('employee_id','department_id')
    def _compute_is_departamento(self):
        for rec in self:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1).id
            rec.is_departamento = True if rec.employee_id.department_id.manager_id.id == employee_id else False

    @api.depends('employee_id','department_id')
    def _compute_is_gerente(self):
        for rec in self:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1).id
            rec.is_gerente = True if rec.employee_id.department_id.gerente.id == employee_id else False
    
    @api.depends('employee_id','department_id','requisiton_responsible_id')
    def _compute_is_responsable(self):
        for rec in self:
            employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1).id
            rec.is_responsable = True if rec.requisiton_responsible_id.id == employee_id else False            
    # @api.model
    # def default_get(self, default_fields):
    #     res = super(MaterialPurchaseRequisition, self).default_get(default_fields)
    #     branch_id = False
    #     if self._context.get('branch_id'):
    #         branch_id = self._context.get('branch_id')
    #     elif self.env.user.branch_id:
    #         branch_id = self.env.user.branch_id.id
    #     res.update({'branch_id' : branch_id})
    #     return res
        
    @api.model
    def _compute_rq_count(self):
        for rq in self:
            rq.count_rq = self.env['stock.picking'].sudo().search_count([('custom_requisition_id', '=', rq.id)])


    count_po = fields.Integer("Requisición de Compra", compute='_compute_po_count')

    @api.model
    def _compute_po_count(self):
        for po in self:
            po.count_po = self.env['purchase.order'].sudo().search_count([('custom_requisition_id', '=', po.id)])

    count_tr = fields.Integer("Licitación de Compra", compute='_compute_tr_count')

    @api.model
    def _compute_tr_count(self):
        for tr in self:
            tr.count_tr = self.env['purchase.agreement'].sudo().search_count([('custom_requisition_id', '=', tr.id)])


    @api.model    
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        vals.update({
            'name': name
            })
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res   

    def requisition_confirm(self):
        for rec in self:
            if not rec.requisition_line_ids:
                raise Warning(_('Por favor, agrega al menos un producto a la requisición.'))
            manager_mail_template = self.env.ref('material_purchase_requisitions.email_confirm_material_purchase_requistion')
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = '1'
            if manager_mail_template:
                manager_mail_template.send_mail(self.id)
            
    def requisition_reject(self):
        for rec in self:
            rec.state = '7'
            rec.reject_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1)
            rec.userreject_date = fields.Date.today()

    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1)
            employee_mail_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition_iruser_custom')
            employee_mail_template.sudo().send_mail(self.id)
            if rec.requisition_type=='internal':
                rec.state = '3'
            else:
                rec.state = '2'

    def user_approve(self):
        for rec in self:
            if not rec.requisition_line_ids:
                raise Warning(_('Por favor, agrega al menos un producto a la requisición.'))
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1)
            email_iruser_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition')
            email_iruser_template.sudo().send_mail(self.id)
            rec.state = '3'

    def reset_draft(self):
        for rec in self:
            rec.state = '0'

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            'analytic_account_id': self.analytic_account_id.id if self.analytic_use == 'header' else line.analytic_account_id.id,
            'product_id' : line.product_id.id,
            'product_uom_qty' : line.qty,
            'product_uom' : line.uom.id,
            'location_id' : self.location_id.id,
            'location_dest_id' : self.dest_location_id.id,
            'name' : line.product_id.name,
            'picking_type_id' : self.custom_picking_type_id.id,
            'picking_id' : stock_id.id,
            'custom_requisition_line_id' : line.id,
            'company_id' : line.requisition_id.company_id.id,
        }
        return pick_vals

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        po_line_vals = {
                'product_id': line.product_id.id,
                'name':line.product_id.name,
                'product_qty': line.qty,
                'product_uom': line.uom.id,
                'date_planned': fields.Date.today(),
                'price_unit': line.product_id.standard_price,
                'order_id': purchase_order.id,
                'analytic_account_id': self.analytic_account_id.id if self.analytic_use == 'header' else line.analytic_account_id.id,
                'custom_requisition_line_id': line.id
        }
        return po_line_vals

    @api.model
    def _prepare_tr_line(self, line=False, tender_order=False):
        tr_line_vals = {
                'sh_product_id': line.product_id.id,
                'sh_qty': line.qty,
                #'product_uom_id': line.uom.id,
                'schedule_date': fields.Date.today(),
                'sh_price_unit': line.product_id.standard_price,
                'agreement_id': tender_order.id,
                'account_analytic_id': self.analytic_account_id.id if self.analytic_use == 'header' else line.analytic_account_id.id,
                'custom_requisition_line_id': line.id
        }
        return tr_line_vals
    
    # MIRA, HONESTAMENTE SOLO HAGO LO QUE PUEDO OK ESTO ERA PARA HOY ASI QUE BUENO SOLO HICE QUE SI SE CUMPLIAN ESAS CONDICIONES LO HICIERA, NO ME PUSE CON GRAN WEBONADA OK, SORRY
    def max_request_stock(self):
        for rec in self:
            if rec.state!="3":
                raise UserError("Esta eligiendo requisiciones no confirmadas en su totalidad")
        # if len(list(set(self.mapped('product_category_id.id'))))>1:
        #     raise UserError("Esta eligiendo requisiciones con distintas categorias de productos")
        self.request_stock()
    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        requisition_obj = self.env['purchase.agreement']
        requisition_line_obj = self.env['purchase.agreement.line']

        internal_obj = self.env['stock.picking.type'].search([('code','=', 'internal')], limit=1)
        internal_obj = self.env['stock.location'].search([('usage','=', 'internal')], limit=1)
        if len(list(set(self.mapped('requisition_type'))))>1:
            raise UserError ("No puede seleccionar requisiciones con diferentes tipos con esta opcion")
        if len(list(set(self.mapped('requisition_type'))))==1 and len(self)>1:
            companies=self.company_id.ids
            licitaciones_id={}
            for company in companies:
                filtered_self=self.filtered(lambda x:x.company_id.id==company)
                tr_vals = {
                    #'vendor_id':rec.partner_id.id,
                    #'currency_id':rec.env.user.company_id.currency_id.id,
                    'sh_order_date':fields.Date.today(),
                    'company_id':company,
                    'custom_requisition_id':filtered_self[-1].id,
                }
                if len(filtered_self.filtered(lambda x: x.name).mapped('name'))>0:
                    tr_vals['sh_source']= ' '.join(filtered_self.filtered(lambda x: x.name).mapped('name'))
                if len(filtered_self.filtered(lambda x: x.reason).mapped('reason'))>0:
                    tr_vals['sh_notes']= ' '.join(filtered_self.filtered(lambda x: x.reason).mapped('reason'))
                requisition_order = requisition_obj.sudo().create(tr_vals)

                #tr_dict.update({partner:requisition_order})
                for line in filtered_self.requisition_line_ids:
                    if line.requisition_type =='tender':
                        line.requisition_id=filtered_self[-1]
                        tr_line_vals = line.requisition_id._prepare_tr_line(line, requisition_order)
                        requisition_line_obj.sudo().create(tr_line_vals)
                        #else:
                        #    requisition_order = tr_dict.get(partner)
                        #    tr_line_vals = rec._prepare_tr_line(line, requisition_order)
                        #    requisition_line_obj.sudo().create(tr_line_vals)
                extratext='las siguientes requisiciones fueron fusionadas con esta para concurso: '
                for rec in filtered_self[:-1]:
                    if rec.reason:
                        rec.reason+=f" --fusionada con requisicion: {filtered_self[-1].name} ID: {filtered_self[-1].id} para concurso de compra --"
                    else:
                        rec.reason=f" --fusionada con requisicion: {filtered_self[-1].name} ID: {filtered_self[-1].id} para concurso de compra --"

                    extratext+=f"{rec.name}, "
                if filtered_self[-1].reason:
                    filtered_self[-1].reason+=extratext
                else:
                    filtered_self[-1].reason=extratext
                for each in filtered_self:
                    each.state = '8'
                    each.rq_create_for = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
                    each.rq_create_for_date = fields.Date.today()
                    each.fused_with_requisition_id=filtered_self[-1]
                    each.fused_with_licitation_id=requisition_order

            
        else:
            for rec in self:
                    if not rec.requisition_line_ids:
                        raise Warning(_('Por favor, agrega al menos un producto a la requisición.'))
                    if any(line.requisition_type =='internal' for line in rec.requisition_line_ids):
                        if not rec.location_id.id:
                                raise Warning(_('Seleccione la ubicación de origen del detalle de pedido.'))
                        if not rec.custom_picking_type_id.id:
                                raise Warning(_('Seleccion el Tipo de salida debajo de los detalles.'))
                        if not rec.dest_location_id:
                            raise Warning(_('Selecciona la ubicación de destino de los detalles de pedido.'))
                        picking_vals = {
                                'partner_id' : rec.employee_id.address_home_id.id,
                                #'min_date' : fields.Date.today(),
                                'location_id' : rec.location_id.id,
                                'location_dest_id' : rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                                'picking_type_id' : rec.custom_picking_type_id.id,#internal_obj.id,
                                'note' : rec.reason,
                                'custom_requisition_id' : rec.id,
                                'origin' : rec.name,
                                'company_id' : rec.company_id.id,
                                
                            }
                        stock_id = stock_obj.sudo().create(picking_vals)
                        delivery_vals = {
                                'delivery_picking_id' : stock_id.id,
                            }
                        rec.write(delivery_vals)
                        rec.state = '4'
                    po_dict = {}
                    tr_dict = {}
                    for line in rec.requisition_line_ids:
                        if line.requisition_type =='internal':
                            pick_vals = rec._prepare_pick_vals(line, stock_id)
                            move_id = move_obj.sudo().create(pick_vals)
                        if line.requisition_type =='purchase':
                            if not line.partner_id:
                                raise Warning(_('Por favor, ingrese al menos un Proveedor(es) para la línea de Requisición'))
                            for partner in line.partner_id:
                                if partner not in po_dict:
                                    po_vals = {
                                        'partner_id':partner.id,
                                        'currency_id':rec.env.company.currency_id.id,
                                        'date_order':fields.Date.today(),
                                        'company_id':rec.company_id.id,
                                        'custom_requisition_id':rec.id,
                                        'origin': rec.name,
                                        'notes': rec.reason,
                                        # 'branch_id': rec.branch_id.id,
                                    }
                                    purchase_order = purchase_obj.create(po_vals)
                                    po_dict.update({partner:purchase_order})
                                    po_line_vals = rec._prepare_po_line(line, purchase_order)
                                    purchase_line_obj.sudo().create(po_line_vals)
                                else:
                                    purchase_order = po_dict.get(partner)
                                    po_line_vals = rec._prepare_po_line(line, purchase_order)
                                    purchase_line_obj.sudo().create(po_line_vals)

                    # Licitación de Compra
                    if line.requisition_type =='tender':
                        #if not line.partner_id:
                        #    raise Warning(_('Por favor, ingrese al menos un Proveedor(es) para la línea de Licitación'))
                        #for partner in line.partner_id:
                            #if partner not in tr_dict:
                        tr_vals = {
                            #'vendor_id':rec.partner_id.id,
                            #'currency_id':rec.env.user.company_id.currency_id.id,
                            'sh_order_date':fields.Date.today(),
                            'company_id':rec.company_id.id,
                            'custom_requisition_id':rec.id,
                            'sh_source': rec.name,
                            'sh_notes': rec.reason,
                        }
                        requisition_order = requisition_obj.sudo().create(tr_vals)
                        #tr_dict.update({partner:requisition_order})
                        for line in rec.requisition_line_ids:
                            if line.requisition_type =='tender':
                                tr_line_vals = rec._prepare_tr_line(line, requisition_order)
                                requisition_line_obj.sudo().create(tr_line_vals)
                                #else:
                                #    requisition_order = tr_dict.get(partner)
                                #    tr_line_vals = rec._prepare_tr_line(line, requisition_order)
                                #    requisition_line_obj.sudo().create(tr_line_vals)
                        rec.state = '4'
                        rec.rq_create_for = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
                        rec.rq_create_for_date = fields.Date.today()
    
    def action_received(self):
        for rec in self:
            rec.receive_date = fields.Date.today()
            rec.recieve_for = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
            rec.recieve_for_date = fields.Date.today()
            rec.state = '5'
    
    def action_cancel(self):
        for rec in self:
            rec.state = '6'
            for agreed in rec.purchase_agreement_ids.filtered(lambda x: not x.purchase_ids or len(x.purchase_ids)==0):

                agreed.action_cancel()
                    
    
    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.department_id.id
            if rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id:
                rec.dest_location_id = rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id 
            
    def show_picking(self):
        for rec in self:
            res = self.env.ref('stock.action_picking_tree_all')
            res = res.read()[0]
            res['domain'] = str([('custom_requisition_id','=',rec.id)])
        return res
        
    def action_show_po(self):
        for rec in self:
            purchase_action = self.env.ref('purchase.purchase_rfq')
            purchase_action = purchase_action.read()[0]
            purchase_action['domain'] = str([('custom_requisition_id','=',rec.id)])
        return purchase_action

    def action_show_tr(self):
        for rec in self:
            purchase_action = self.env.ref('sh_po_tender_management.sh_purchase_agreement_action')
            purchase_action = purchase_action.read()[0]
            purchase_action['domain'] = str([('custom_requisition_id','=',rec.id)])
        return purchase_action
#endregion

