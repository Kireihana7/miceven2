# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api,_
from odoo.exceptions import UserError
from datetime import datetime

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        super(MailComposeMessage, self).action_send_mail()
        if self.env.context.get('active_model') == 'purchase.agreement' and self.env.context.get('active_id'):
            tender_id = self.env['purchase.agreement'].sudo().browse(self.env.context.get('active_id'))
            if tender_id and self.partner_ids and self.env.company.sh_auto_add_followers:
                tender_id.message_subscribe(self.partner_ids.ids)
                

class ShPurchaseAgreement(models.Model):
    _name='purchase.agreement'
    _description='Purchase Agreement'
    _rec_name='name'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    def get_deafult_company(self):
        company_id = self.env.company
        return company_id
    
    def _default_picking_type_id(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1).in_type_id.id

    name = fields.Char('Name',readonly=True,track_visibility="onchange")
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('bid_selection','Bid Selection'),('closed','Closed'),('cancel','Cancelled')],string="State",default='draft',track_visibility="onchange")
    rfq_count = fields.Integer("Received Quotations",compute='get_rfq_count')
    order_count = fields.Integer("Selected Orders",compute='get_order_count')
    sh_purchase_user_id = fields.Many2one('res.users','Purchase Representative',track_visibility="onchange")
    sh_agreement_type = fields.Many2one('purchase.agreement.type','Tender Type',required=False,track_visibility="onchange")
    sh_vender_id = fields.Many2one('res.partner','Vendor',track_visibility="onchange")
    partner_id = fields.Many2one('res.partner','Partner')
    partner_ids = fields.Many2many('res.partner',string='Vendors',track_visibility="onchange")
    user_id = fields.Many2one('res.users','User')
    sh_agreement_deadline = fields.Datetime('Tender Deadline',track_visibility="onchange")
    sh_order_date = fields.Date('Ordering Date',track_visibility="onchange")
    sh_delivery_date = fields.Date('Delivery Date',track_visibility="onchange")
    sh_source = fields.Char('Source Document',track_visibility="onchange")
    sh_notes = fields.Text("Terms & Conditions",track_visibility="onchange")
    sh_purchase_agreement_line_ids = fields.One2many('purchase.agreement.line','agreement_id',string='Purchase Agreement Line')
    purchase_ids  = fields.One2many('purchase.order','agreement_id',string='Purchase Order')
    company_id = fields.Many2one('res.company',string="Company", default=get_deafult_company)
    compute_custom_boolean = fields.Boolean(compute='_compute_module_boolean')
    #currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Operation Type',
        default=_default_picking_type_id,
        domain="[('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)]",
        ondelete='restrict')
    def _compute_module_boolean(self):
        if self:
            for rec in self:
                rec.compute_custom_boolean = False
                portal_module_id = self.env['ir.module.module'].sudo().search([('name','=','sh_po_tender_portal'),('state','in',['installed'])],limit=1)
                if portal_module_id:
                    rec.compute_custom_boolean = True
    
    
    def _compute_access_url(self):
        super(ShPurchaseAgreement, self)._compute_access_url()
        for tender in self:
            tender.access_url = '/my/tender/%s' % (tender.id)
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Tender', self.name)
    
    
    def get_rfq_count(self):
        if self:
            for rec in self:
                purchase_orders = self.env['purchase.order'].sudo().search([('agreement_id','=',rec.id),('state','in',['draft','cancel','sent']),('selected_order','=',False)])
                if purchase_orders:
                    rec.rfq_count = len(purchase_orders.ids)
                else:
                    rec.rfq_count = 0
    
    def get_order_count(self):
        if self:
            for rec in self:
                purchase_orders = self.env['purchase.order'].sudo().search([('agreement_id','=',rec.id),('state','not in',['cancel']),('selected_order','=',True)])
                if purchase_orders:
                    rec.order_count = len(purchase_orders.ids)
                else:
                    rec.order_count = 0
    
    @api.model    
    def create(self, vals):
        Sequence = self.env['ir.sequence']
        COMPANY = self.env.company
        CODE = "purchase.agreement"

        if not Sequence.search([("code", "=", CODE),("company_id", "=", COMPANY.id)]):
            Sequence.create({
                "code": CODE,
                "prefix": "TE",
                'name': "Purchase Agreement Sequence",
                'padding': 4,
                'company_id': COMPANY.id,
            })

        name = Sequence.next_by_code(CODE)
        vals.update({
            'name': name
            })
        res = super(ShPurchaseAgreement, self).create(vals)
        return res    

    def action_confirm_auto(self):
        for rec in self:
            if len(rec.partner_ids) == 0:
                raise UserError('Debe añadir al menos un Proveedor')
            for partner in rec.partner_ids:
                if not rec.sh_agreement_type:
                    raise UserError('Seleccione el Tipo de Concurso')
                line_ids = []
                current_date = None
                if rec.sh_delivery_date:
                    current_date = rec.sh_delivery_date
                else:
                    current_date = fields.Datetime.now()
                purchase_order_obj = self.env['purchase.order']
                purchase_order_obj = purchase_order_obj.create({
                    'partner_id': partner.id,
                    'date_order': datetime.now(),
                    'origin': rec.sh_source,
                    'agreement_id':rec.id,
                    'user_id': rec.sh_purchase_user_id.id,
                    'company_id':rec.company_id.id,
                    'picking_type_id':self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', rec.company_id.id)],limit=1).id
                })
                
                for rec_line in rec.sh_purchase_agreement_line_ids:
                    purchase_product_matrix_module = self.env['ir.module.module'].sudo().search([('name','=','purchase_product_matrix'),('state','=','installed')],limit=1)
                    if purchase_product_matrix_module:
                        line_vals={
                            'product_id':rec_line.sh_product_id.id,
                            'name':rec_line.sh_product_id.name_get()[0][1],
                            'product_template_id':rec_line.sh_product_id.product_tmpl_id.id,
                            'date_planned':current_date,
                            'product_qty':rec_line.sh_qty,
                            'status':'draft',
                            'agreement_id':rec.id,
                            'product_uom':rec_line.sh_product_id.uom_id.id,
                            'price_unit':rec_line.sh_price_unit,
                            'account_analytic_id': rec_line.account_analytic_id.id,
                            'analytic_tag_ids': rec_line.analytic_tag_ids.ids,
                            }
                    else:
                        line_vals={
                            'product_id':rec_line.sh_product_id.id,
                            'name':rec_line.sh_product_id.name_get()[0][1],
                            'date_planned':current_date,
                            'product_qty':rec_line.sh_qty,
                            'status':'draft',
                            'agreement_id':rec.id,
                            'product_uom':rec_line.sh_product_id.uom_id.id,
                            'price_unit':rec_line.sh_price_unit,
                            'account_analytic_id': rec_line.account_analytic_id.id,
                            'analytic_tag_ids': rec_line.analytic_tag_ids.ids,
                            }

                    line_ids.append((0,0,line_vals))
                purchase_order_obj.order_line = line_ids
                purchase_order_obj.onchange_partner_id()
                purchase_order_obj.order_line._compute_tax_id()
                rec.state ='confirm'

    def action_confirm(self):
        if self:
            for rec in self:
                if not rec.sh_agreement_type:
                    raise UserError('Seleccione el Tipo de Concurso')
                rec.state ='confirm'

    def action_new_quotation(self):
        if self:
            for rec in self:
                line_ids = []
                current_date = None
                if rec.sh_delivery_date:
                    current_date = rec.sh_delivery_date
                else:
                    current_date = fields.Datetime.now()
                for rec_line in rec.sh_purchase_agreement_line_ids:
                    purchase_product_matrix_module = self.env['ir.module.module'].sudo().search([('name','=','purchase_product_matrix'),('state','=','installed')],limit=1)
                    if purchase_product_matrix_module:
                        line_vals={
                            'product_id':rec_line.sh_product_id.id,
                            'name':rec_line.sh_product_id.name_get()[0][1],
                            'product_template_id':rec_line.sh_product_id.product_tmpl_id.id,
                            'date_planned':current_date,
                            'product_qty':rec_line.sh_qty,
                            'status':'draft',
                            'agreement_id':rec.id,
                            'product_uom':rec_line.sh_product_id.uom_id.id,
                            'price_unit':rec_line.sh_price_unit,
                            'account_analytic_id': rec_line.account_analytic_id.id,
                            'analytic_tag_ids': rec_line.analytic_tag_ids.ids,
                            }
                        line_ids.append((0,0,line_vals))
                    else:
                        line_vals={
                            'product_id':rec_line.sh_product_id.id,
                            'name':rec_line.sh_product_id.name_get()[0][1],
                            'date_planned':current_date,
                            'product_qty':rec_line.sh_qty,
                            'status':'draft',
                            'agreement_id':rec.id,
                            'product_uom':rec_line.sh_product_id.uom_id.id,
                            'price_unit':rec_line.sh_price_unit,
                            'account_analytic_id': rec_line.account_analytic_id.id,
                            'analytic_tag_ids': rec_line.analytic_tag_ids.ids,
                            }
                        line_ids.append((0,0,line_vals))
                return {
                    'name': _('New'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order',
                    'view_type':'form',
                    'view_mode': 'form',
                    'context':{'default_origin':rec.sh_source,'default_agreement_id':rec.id,'default_user_id':rec.sh_purchase_user_id.id,'default_order_line':line_ids},
                    'target':'current'
                    }

    def action_validate(self):
        if self:
            for rec in self:
                if self.env.company.sh_auto_add_followers and rec.partner_ids:
                    rec.message_subscribe(rec.partner_ids.ids)
                if self.env.company.sh_portal_user_create and rec.partner_ids:
                    for vendor in rec.partner_ids:
                        user_id = self.env['res.users'].sudo().search([('partner_id','=',vendor.id)],limit=1)
                        if not user_id:
                            portal_wizard_obj = self.env['portal.wizard']
                            created_portal_wizard =  portal_wizard_obj.create({})
                            if created_portal_wizard and vendor.email and self.env.user:
                                portal_wizard_user_obj = self.env['portal.wizard.user']
                                wiz_user_vals = {
                                    'wizard_id': created_portal_wizard.id,
                                    'partner_id': vendor.id,
                                    'email' : vendor.email,
                                    'in_portal' : True,
                                    'user_id' : self.env.user.id,
                                    }
                                created_portal_wizard_user = portal_wizard_user_obj.create(wiz_user_vals)
                                if created_portal_wizard_user:
                                    created_portal_wizard.action_apply()
                                    vendor_portal_user_id = self.env['res.users'].sudo().search([('partner_id','=',vendor.id)],limit=1)
                                    if vendor_portal_user_id:
                                        vendor_portal_user_id.is_tendor_vendor = True
                rec.state='bid_selection'

    def action_analyze_rfq(self):
        list_id = self.env.ref('sh_po_tender_management.sh_bidline_tree_view').id
        form_id = self.env.ref('sh_po_tender_management.sh_bidline_form_view').id
        pivot_id = self.env.ref('sh_po_tender_management.purchase_order_line_pivot_custom').id
        return {
                'name': _('Tender Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order.line',
                'view_type':'form',
                'view_mode': 'tree,pivot,form',
                'views': [(list_id, 'tree'),(pivot_id, 'pivot'),(form_id,'form')],
                'domain':[('agreement_id','=',self.id),('state','not in',['cancel']),('order_id.selected_order','=',False)],
                'context':{'search_default_groupby_product':1},
                'target':'current'
            }
    
    def action_set_to_draft(self):
        if self:
            for rec in self:
                rec.state='draft'
                
    def action_close(self):
        if self:
            for rec in self:
                rec.state='closed'
    def action_cancel(self):
        if self:
            for rec in self:
                rec.state='cancel'
    
    def action_send_tender(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('sh_po_tender_management', 'email_template_edi_purchase_tedner')[1]
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx={
            'default_model': 'purchase.agreement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
            }
        if self.sh_vender_id:
            ctx.update({
              'default_partner_ids':[(6,0,self.sh_vender_id.ids)]  
            })
        if self.partner_ids:
            ctx.update({
              'default_partner_ids':[(6,0,self.partner_ids.ids)]  
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    def action_view_quote(self):
        return {
                'name': _('Received Quotations'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_type':'form',
                'view_mode': 'tree,form',
                'res_id':self.id,
                'context':{'default_origin':self.sh_source},
                'domain':[('agreement_id','=',self.id),('selected_order','=',False),('state','in',['draft','cancel'])],
                'target':'current'
            }
        
    def action_view_order(self):
        return {
                'name': _('Selected Orders'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_type':'form',
                'view_mode': 'tree,form',
                'res_id':self.id,
                'context':{'default_origin':self.sh_source},
                'domain':[('agreement_id','=',self.id),('selected_order','=',True),('state','not in',['cancel'])],
                'target':'current'
            }
        
class ShPurchaseAgreementLine(models.Model):
    _name='purchase.agreement.line'
    _description="Purchase Agreement Line"
    
    agreement_id = fields.Many2one('purchase.agreement','Purchase Tender')
    sh_product_id = fields.Many2one('product.product','Product',required=True)
    sh_qty = fields.Float('Quantity',default=1.0)
    sh_ordered_qty = fields.Float('Ordered Quantities',compute='get_ordered_qty')
    sh_price_unit = fields.Float('Unit Price')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    schedule_date = fields.Date(string='Scheduled Date')
    company_id = fields.Many2one(related="agreement_id.company_id",string="Company")

    def get_ordered_qty(self):
        if self:
            for rec in self:
                order_qty =0.0
                purchase_order_lines = self.env['purchase.order.line'].sudo().search([('product_id','=',rec.sh_product_id.id),('agreement_id','=',rec.agreement_id.id),('order_id.selected_order','=',True),('order_id.state','in',['purchase'])])
                for line in purchase_order_lines:
                    order_qty+=line.product_qty
                rec.sh_ordered_qty = order_qty
    