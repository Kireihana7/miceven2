# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    tiene_deuda = fields.Boolean(string="Tiene Deuda Pendiente",compute="_compute_tiene_deuda")
    monto_deuda_total_nv = fields.Float(string="Monto Deuda Total No Vencido")
    monto_deuda_total = fields.Float(string="Monto Deuda Total")
    corporativo = fields.Boolean(related="partner_id.corporativo")
    fecha_pagada = fields.Date(string="Fecha de de Pago",default=False,readonly=True,compute="_compute_fecha_pagada",store=True,tracking=True)
    dias_pago = fields.Integer(string="Días de Pago",compute="_compute_fecha_pagada",default=False,store=True)
    
    def open_current_invoice_residual(self):
        self.ensure_one()
        account_obj = self.env['account.move'].sudo()
        domain_vc = [
                ('corporativo','=',False),
                ('amount_residual','>',0),
                ('state','=','posted'),
                ('move_type','=','out_invoice'),
                ('company_id','=',self.company_id.id),
                ('invoice_date_due','<=',date.today()),
                ('invoice_user_id','=',self.env.user.id),
            ]
        if self.partner_id.parent_id:
            domain_vc.append(('partner_id','child_of', self.partner_id.parent_id.id))
        else:
            domain_vc.append(('partner_id','child_of', self.partner_id.id))
        facturas = account_obj.search(domain_vc)
        if len(account_obj.search(domain_vc))==0:
            raise UserError('No existen facturas por pagar de este cliente')
        res = self.env.ref('account.action_move_out_invoice_type')
        res = res.read()[0]
        res['domain'] = str([('id', 'in', facturas.mapped('id'))])
        res['context'] = {'delete':False,'create':False,'edit':False,'duplicate':False}
        return res

    @api.depends('amount_residual','invoice_date')
    def _compute_fecha_pagada(self):
        for rec in self:
            if not rec.fecha_pagada and rec.amount_residual == 0:
                rec.fecha_pagada = date.today()
                rec.dias_pago = int((date.today() - (rec.invoice_date or rec.date)).days)

    @api.depends('partner_id','company_id')
    def _compute_tiene_deuda(self):
        for rec in self:
            rec.tiene_deuda = False
            rec.monto_deuda_total = 0
            rec.monto_deuda_total_nv = 0
            domain_nv = [
                ('corporativo','=',False),
                ('amount_residual','>',0),
                ('state','=','posted'),
                ('move_type','=','out_invoice'),
                ('company_id','=',rec.company_id.id),
                ('invoice_date_due','>',date.today()),
            ]
            domain_vc = [
                ('corporativo','=',False),
                ('amount_residual','>',0),
                ('state','=','posted'),
                ('move_type','=','out_invoice'),
                ('company_id','=',rec.company_id.id),
                ('invoice_date_due','<=',date.today()),
            ]  
            account_obj = self.env['account.move'].sudo()
            if rec.partner_id.parent_id:
                domain_nv.append(('partner_id','child_of', rec.partner_id.parent_id.id))
                domain_vc.append(('partner_id','child_of', rec.partner_id.parent_id.id))
            else:
                domain_nv.append(('partner_id','child_of', rec.partner_id.id))
                domain_vc.append(('partner_id','child_of', rec.partner_id.id))
            ventas = sum(account_obj.search(domain_nv).filtered(lambda x: x.currency_id == x.company_id.currency_id).mapped('amount_residual')) + sum(account_obj.search(domain_nv).filtered(lambda x: x.currency_id != x.company_id.currency_id).mapped('amount_residual_signed_ref'))
            if ventas > 0:
                rec.tiene_deuda = True
                rec.monto_deuda_total_nv = round(ventas,2)
              
            ventas_vc = sum(account_obj.search(domain_vc).filtered(lambda x: x.currency_id == x.company_id.currency_id).mapped('amount_residual')) + sum(account_obj.search(domain_vc).filtered(lambda x: x.currency_id != x.company_id.currency_id).mapped('amount_residual_signed_ref'))
            if ventas_vc > 0: 
            	rec.tiene_deuda = True
            	rec.monto_deuda_total = round(ventas_vc,2)