# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class GeneratePurchaseWiazrd(models.TransientModel):
    _name = "generate.purchase"
    _description = "Create Purchase Wizard"
    
    new_order_id = fields.Many2one('purchase.order', string="Quantity")

    def action_generate_po(self):
        inverse_approve = []
        res_id = self.env["purchase.order.line"].browse(self._context.get('active_ids',[]))
        res_obj = self.env['purchase.order'].sudo()
        res_obj_line = self.env['purchase.order.line'].sudo()
        tr_dict = {}
        tr_vals = {}
        partner_ids = [] #listado de product_id unicos
        for invoices in res_id.order_id.partner_id.sorted(key=lambda m: m.id):
            # verifica si existe el producto en la lista
            if invoices.id not in partner_ids:
                partner_ids.append(invoices.id)

        #Licitación de Compra
        for id in partner_ids:
            for partner in res_id.filtered(lambda m: m.order_id.partner_id.id == id and m.state_id == 'confirm'):
                if partner.state_id != 'confirm':
                    raise UserError(_('Por favor, confirme el Acuerdo de Compra'))
                tr_vals = {
                    'partner_id':partner.order_id.partner_id.id,
                    'requisition_id':partner.order_id.requisition_id.id,
                    'origin':partner.order_id.origin,
                    'user_id':partner.order_id.user_id.id,
                    'winner':True,
                }
            if tr_vals != {}:
                requisition_order = res_obj.create(tr_vals)
                tr_dict.update({partner:requisition_order})
            for x in res_id.filtered(lambda m: m.order_id.partner_id.id == id and m.state_id == 'confirm'):
                tr_line_vals = self._prepare_tr_line(x, requisition_order)
                res_obj_line.sudo().create(tr_line_vals)
        inverse_approve.append(x.order_id.requisition_id.id)    
        return {
            'name': 'Adjudicadas',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_type':'form',
            'view_mode': 'tree,form',
            'domain': [('requisition_id','in',inverse_approve),('winner','=',True)],
        }

    @api.model
    def _prepare_tr_line(self, line=False, tender_order=False):
        tr_line_vals = {
        'name':line.product_id.name,
        'product_id': line.product_id.id,
        'product_qty': line.product_qty,
        'date_planned':datetime.now(),
        'product_uom': line.product_uom[0].id,
        'price_unit': line.price_unit,
        'order_id':  tender_order.id,
        }
        return tr_line_vals

    # def action_generate_po(self):
    #     inverse_approve = []
    #     res_id = self.env["purchase.order.line"].browse(self._context.get('active_ids',[]))
    #     res_obj = self.env['purchase.order'].sudo()
    #     for x in res_id:
    #         if x.state_id != 'confirm':
    #             raise UserError(('Please confirm purchase bid'))
    #         else:
    #             rep = res_obj.create({
    #                     'partner_id':x.order_id.partner_id.id,
    #                     'requisition_id':x.order_id.requisition_id.id,
    #                     'origin':x.order_id.origin,
    #                     'user_id':x.order_id.user_id.id,
    #                     'order_line': [
    #                             (0, 0, {
    #                                 'name':x.product_id.name,
    #                                 'product_id': x.product_id.id,
    #                                 'product_qty': x.product_qty,
    #                                 'date_planned':datetime.now(),
    #                                 'product_uom': x.product_uom[0].id,
    #                                 'price_unit': x.price_unit,
    #                             })
    #                         ]
    #                     })
    #             inverse_approve.append(x.order_id.requisition_id.id)    
    #     return {
    #         'name': 'Approved',
    #         'res_model': 'purchase.order',
    #         'type': 'ir.actions.act_window',
    #         'view_type':'form',
    #         'view_mode': 'tree,form',
    #         'domain': [('requisition_id','in',inverse_approve)],
    #     }