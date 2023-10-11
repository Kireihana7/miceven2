# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    farmer_request_id = fields.Many2one(
        'farmer.cropping.request',
        string='Crop Request',
        readonly=True,
        copy=False,
        tracking=True
    )

    use_project = fields.Boolean(
        string='Use Activities Template'
    )       

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=False,
        copy=False,
        tracking=True
    )       

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=False,
        readonly=True,
        copy=False,
        tracking=True
    )       
    
    # Modificación: Campo opcional.
    analytic_use = fields.Selection([
        ('header', 'Por único seleccionado'),
        ('line', 'Por líneas')],
        string='Centro de Costo a Utilizar', 
        default='header',
        required=True,
        tracking=True
    )

    # Modificación: Cuenta Analítica Padre.
    parent_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        # required=True,
        string='Parent Analytical Account',
        copy=True,
        tracking=True
    )

    # Modificación: Campo opcional.
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        required=False,
        string='Centro de Costo',
        copy=True,
        tracking=True
    )

    analytic_account_header_id_1 = fields.Many2one(
        'account.analytic.account',
        string='Finca',
        tracking=True
    )

    analytic_account_header_id_2 = fields.Many2one(
        'account.analytic.account',
        string='Actividad',
        # required=True,
        tracking=True
    )        

    analytic_account_header_id_3 = fields.Many2one(
        'account.analytic.account',
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_header_id_4 = fields.Many2one(
        'account.analytic.account',
        string='Tablón',
        required=False,
        tracking=True
    )      

    crop_request_transaction_id = fields.Many2one('crop.request.transaction', string='Crop Request Transaction', required=False, tracking=True)
    crop_request_transaction_line_id = fields.Integer('Transaction Line', tracking=True)

    agriculture_company = fields.Boolean(related='company_id.agriculture_company')

    requisition_agriculture_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        string='Líneas de Requisiciones (agricultura)',
        copy=True,tracking=True
    )
    @api.onchange('use_project')
    def _onchange_use_project(self):
        domain = [('type', '=', 'activity')]
        if self.use_project:
            if self.project_id:
                domain = [('task_id', 'in', self.project_id.task_ids.ids)]
        # raise UserError(_(domain))
        return {
            'domain': { 
                'analytic_account_header_id_2': domain
            }
        }   

    @api.onchange('project_id')
    def _onchange_project_id(self):
        domain = [('type', '=', 'activity')]
        if self.use_project:
            if self.project_id:
                domain = [('task_id', 'in', self.project_id.task_ids.ids)]
        # raise UserError(_(domain))
        return {
            'domain': { 
                'analytic_account_header_id_2': domain
            }
        }   

    @api.onchange('analytic_account_header_id_2')
    def _onchange_analytic_account_header_id_2(self):
        domain = [('type', '=', 'activity')]
        if self.use_project:
            if self.project_id:
                domain = [('task_id', 'in', self.project_id.task_ids.ids)]
        # raise UserError(_(domain))
        return {
            'domain': { 
                'analytic_account_header_id_2': domain
            }
        }    

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
            'company_id': line.requisition_id.company_id.id,
            'custom_requisition_line_id' : line.id,
        }
        # Versión agrícola:
        if self.company_id.agriculture_company:
            crop_request_transaction_id = False
            if line.crop_request_transaction_id:
                crop_request_transaction_id = line.crop_request_transaction_id.id

            pick_vals.update({
                'crop_request_transaction_id': crop_request_transaction_id,
                'crop_request_transaction_line_id' : line.crop_request_transaction_line_id,
                'analytic_account_id_1': self.analytic_account_header_id_1.id if self.analytic_use == 'header' else line.analytic_account_id_1.id,
                'analytic_account_id_2': self.analytic_account_header_id_2.id if self.analytic_use == 'header' else line.analytic_account_id_2.id,
                'analytic_account_id_3': self.analytic_account_header_id_3.id if self.analytic_use == 'header' else line.analytic_account_id_3.id,
                'analytic_account_id_4': self.analytic_account_header_id_4.id if self.analytic_use == 'header' else line.analytic_account_id_4.id,
            })

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
        # Versión agrícola:
        if self.company_id.agriculture_company:        
            po_line_vals.update({
                # 'custom_requisition_line_id': line.id,
                'analytic_account_id_1': self.analytic_account_header_id_1.id if self.analytic_use == 'header' else line.analytic_account_id_1.id,
                'analytic_account_id_2': self.analytic_account_header_id_2.id if self.analytic_use == 'header' else line.analytic_account_id_2.id,
                'analytic_account_id_3': self.analytic_account_header_id_3.id if self.analytic_use == 'header' else line.analytic_account_id_3.id,
                'analytic_account_id_4': self.analytic_account_header_id_4.id if self.analytic_use == 'header' else line.analytic_account_id_4.id,
            })
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
        
        # Versión agrícola:
        if self.company_id.agriculture_company:               
            farmer_request_id = False
            if line.farmer_request_id:
                farmer_request_id = line.farmer_request_id.id

            crop_request_transaction_id = False
            if line.crop_request_transaction_id:
                crop_request_transaction_id = line.crop_request_transaction_id.id
            
            crop_request_transaction_line_id = 0
            if line.crop_request_transaction_line_id:
                crop_request_transaction_line_id = line.crop_request_transaction_line_id

            tr_line_vals.update({
                'farmer_request_id': farmer_request_id,
                'crop_request_transaction_id': crop_request_transaction_id,
                'crop_request_transaction_line_id': crop_request_transaction_line_id,
                'analytic_account_id_1': line.analytic_account_id_1.id,
                'analytic_account_id_2': line.analytic_account_id_2.id,
                'analytic_account_id_3': line.analytic_account_id_3.id,
                'analytic_account_id_4': line.analytic_account_id_4.id
            })    
        return tr_line_vals        

    def user_approve(self):
        for rec in self:
            # Si no se trata de una empresa agrícola, que ejecute su funcionamiento por defecto:
            if rec.company_id.agriculture_company == False:
                super(MaterialPurchaseRequisition, self).user_approve()
            else:
                # Versión agrícola:
                line_ids = rec.requisition_agriculture_line_ids    

                if not line_ids:
                    raise UserError(_('Por favor, agrega al menos un producto a la requisición.'))
                rec.userrapp_date = fields.Date.today()
                rec.approve_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid),('company_id', '=', self.env.company.id)], limit=1)
                email_iruser_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition')
                email_iruser_template.sudo().send_mail(self.id)
                rec.state = '3'    

    def requisition_confirm(self):
        for rec in self:
            # Si no se trata de una empresa agrícola, que ejecute su funcionamiento por defecto:
            if rec.company_id.agriculture_company == False:
                super(MaterialPurchaseRequisition, self).requisition_confirm()
            else:
                # Versión agrícola:
                line_ids = rec.requisition_agriculture_line_ids
                if not line_ids:
                    raise UserError(_('Por favor, agrega al menos un producto a la requisición.'))
                manager_mail_template = self.env.ref('material_purchase_requisitions.email_confirm_material_purchase_requistion')
                rec.employee_confirm_id = rec.employee_id.id
                rec.confirm_date = fields.Date.today()
                rec.state = '1'
                if manager_mail_template:
                    manager_mail_template.send_mail(self.id)

                # Centros de Costo:
                # raise UserError(_(f'Analytic Use: {rec.analytic_use}; ID: {self.id}'))
                for line in line_ids:
                    #material_purchase_requisition_line_obj = self.env['material.purchase.requisition.line'].search([('requisition_id', '=', self.id)])

                    a1 = rec.analytic_account_header_id_1.id
                    a2 = rec.analytic_account_header_id_2.id
                    a3 = rec.analytic_account_header_id_3.id
                    a4 = rec.analytic_account_header_id_4.id

                    if rec.analytic_use == 'line':
                        a1 = line.analytic_account_id_1.id
                        a2 = line.analytic_account_id_2.id
                        a3 = line.analytic_account_id_3.id
                        a4 = line.analytic_account_id_4.id                    
                        
                    farmer_request_id = False
                    if rec.farmer_request_id:
                        farmer_request_id = rec.farmer_request_id.id
                        
                    line.sudo().write({
                        'farmer_request_id': farmer_request_id,
                        'analytic_account_id_1': a1,
                        'analytic_account_id_2': a2,
                        'analytic_account_id_3': a3,
                        'analytic_account_id_4': a4,
                    })    

    def request_stock(self):
        for rec in self:
            # Si no se trata de una empresa agrícola, que ejecute su funcionamiento por defecto:
            if rec.company_id.agriculture_company == False:
                super(MaterialPurchaseRequisition, self).request_stock()
            else:
                # Versión agrícola:
                stock_obj = self.env['stock.picking']
                move_obj = self.env['stock.move']
                purchase_obj = self.env['purchase.order']
                purchase_line_obj = self.env['purchase.order.line']

                requisition_obj = self.env['purchase.agreement']
                requisition_line_obj = self.env['purchase.agreement.line']
                for rec in self:
                    line_ids = rec.requisition_agriculture_line_ids    

                    if not line_ids:
                        raise UserError(_('Por favor, agrega al menos un producto a la requisición.'))
                    if any(line.requisition_type =='internal' for line in line_ids):
                        if not rec.location_id.id:
                                raise UserError(_('Seleccione la ubicación de origen del detalle de pedido.'))
                        if not rec.custom_picking_type_id.id:
                                raise UserError(_('Seleccion el Tipo de salida debajo de los detalles.'))
                        if not rec.dest_location_id:
                            raise UserError(_('Selecciona la ubicación de destino de los detalles de pedido.'))
                        
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
                    for line in line_ids:
                        if line.requisition_type =='internal':
                            pick_vals = rec._prepare_pick_vals(line, stock_id)
                            move_id = move_obj.sudo().create(pick_vals)
                        if line.requisition_type =='purchase':
                            if not line.partner_id:
                                raise UserError(_('Por favor, ingrese al menos un Proveedor(es) para la línea de Requisición'))
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

                    # Licitación de Compra:
                    counter_tender_lines = 0
                    for line in line_ids:
                        if line.requisition_type == 'tender':
                            counter_tender_lines += 1
                    
                    if counter_tender_lines > 0:
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
                        for line in line_ids:
                            # Licitación de Compra
                            if line.requisition_type == 'tender':
                                tr_line_vals = rec._prepare_tr_line(line, requisition_order)
                                # raise UserError(_(f'tr_line_vals: {tr_line_vals}'))
                                requisition_line_obj.sudo().create(tr_line_vals)

                    rec.state = '4'
                    rec.rq_create_for = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
                    rec.rq_create_for_date = fields.Date.today()