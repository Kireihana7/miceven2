# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api,_
from odoo.exceptions import UserError
from datetime import datetime

class ShPurchaseAgreement(models.Model):
    _inherit='purchase.agreement'

    

    state = fields.Selection(selection_add=[('fusion', 'Fusionada')],ondelete={'fusion':'set default'},default='draft',track_visibility="onchange")
    fusion_materials=fields.One2many("purchase.agreement","fusion_target",string="Fusionada apartir de")
    fusion_target=fields.Many2one("purchase.agreement",string="Fusionada en")
    def action_fuse_agreement(self):
        if self.filtered(lambda x:x.state in ['cancel','closed']):
            raise UserError("No puede fusionar acuerdos de compra Cerrados o Cancelados")
        if len(self.mapped("sh_purchase_user_id"))>1:
            raise UserError("No puede fusionar acuerdos de compra de distintos representantes")
        if len(self.mapped("sh_agreement_type"))>1:
            raise UserError("No puede fusionar acuerdos de compra de distintos tipos")

        extra_agreement=self.env['purchase.agreement'].create({
                                                                'sh_purchase_user_id':self.sh_purchase_user_id[:1].id if self.sh_purchase_user_id[:1] else False,
                                                                'sh_agreement_type':self.sh_agreement_type[:1].id if self.sh_agreement_type[:1] else False,

        })
        extra_agreement.partner_ids=self.partner_ids
        product_quantity_tuples={}
        for line in self.sh_purchase_agreement_line_ids:
            line.agreement_id=extra_agreement
            # if not product_quantity_tuples.get(f"{line.sh_product_id.id}",False):
            #     product_quantity_tuples[line.sh_product_id.id]=line.sh_qty
            # else:
            #     product_quantity_tuples[line.sh_product_id.id]=product_quantity_tuples[line.sh_product_id.id]+line.sh_qty
        # for line_pro in product_quantity_tuples:
            # if not extra_agreement.sh_purchase_agreement_line_ids:
            #     extra_agreement.sh_purchase_agreement_line_ids=self.env['purchase.agreement.line'].create({'sh_product_id'})
        extra_agreement
        for rec in self:
            rec.state="fusion"
            rec.fusion_target=extra_agreement
    def action_close(self):
        if self:
            for rec in self:
                rec.state='closed'
    def action_cancel(self):
        if self:
            for rec in self:
                rec.state='cancel'
    
    
    
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
    _inherit='purchase.agreement.line'
    