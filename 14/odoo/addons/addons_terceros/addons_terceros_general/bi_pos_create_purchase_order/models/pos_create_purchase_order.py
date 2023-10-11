# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import Warning,UserError
import random
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class PosConfigInherit(models.Model):
    _inherit = "pos.config"

    create_po = fields.Boolean(string="Create Purchase Order")
    po_state = fields.Selection([('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked')], string="PO State", default='draft')


class pos_create_purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    po_pos = fields.Boolean(string="POS Order",default=False)

    def create_purchase_order_ui(self, partner_id, orderlines,cashier_id,po_state,session_id):
        
        shop_name = self.env['pos.session'].search([('id','=', session_id)]).name
        po_line_obj = self.env['purchase.order.line']
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id  
        else:
            raise UserError('Debe tener una sucursal seleccionada')
        picking_type_id = self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
        order_id = self.create({'partner_id': partner_id,'user_id':cashier_id,'origin':shop_name,'po_pos':True,'branch_id':branch_id,'picking_type_id':picking_type_id.id,})
        for dict_line in orderlines:
            product_obj = self.env['product.product'] 
            product_dict  = dict_line.get('product')
            
            product_tax = product_obj.browse(product_dict .get('id'))   
            tax_ids = []
            for tax in product_tax.taxes_id:
                tax_ids.append(tax.id)
           

            product_name =product_obj.browse(product_dict .get('id')).name  
            vals = {'product_id': product_dict.get('id'),
                    'name':product_name,
                    'product_qty': product_dict.get('quantity'),
                    'price_unit':product_dict.get('price'),
                    'product_uom':product_dict.get('uom_id'),
                    'taxes_id': [(6,0,tax_ids)],
                    'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'order_id': order_id.id}
            po_line_obj.create(vals)
        if order_id:
            if po_state == "sent":
                template_id = self.env.ref('purchase.email_template_edi_purchase').id
                template = self.env['mail.template'].browse(template_id)
                active_id = self.env['purchase.order'].browse(order_id.id)
                if active_id:
                    active_id.action_rfq_send()
                    template.send_mail(active_id.id,force_send=True)
                    active_id.write({'state':'sent'})
            if po_state == "purchase":
                
                order_id.sudo().button_confirm()
                order_id.write({'state':'purchase'})
                
            if po_state == "to approve":
                self.browse(order_id.id).write({'state': 'to approve'})
                
            if po_state =="done":
                order_id.button_confirm()
                order_id.write({'state':'purchase'})
                order_id.button_done()
                order_id.write({'state':'done'})
                

        return True

