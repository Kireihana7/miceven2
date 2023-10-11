# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPaymentFast(models.Model):
    _name = 'account.payment.fast'
    _description = 'Pago Rapido'
    _order = 'create_date desc'
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",default='/',readonly=True)
    state = fields.Selection([ 
        ('cancel', 'Cancelado'),
        ('draft', 'Borrador'),
        ('done', 'Realizado'),
        ('payment', 'Pagos Creados')],
        default='draft',
        readonly=1,
        string='Estatus',
        tracking=True,
    )
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users',string="Vendedor",default=lambda self: self.env.user)
    confirmed_by = fields.Many2one('res.users',string="Confirmado por",readonly=True)
    payment_create_by = fields.Many2one('res.users',string="Pagos creados por",readonly=True)
    order_line = fields.One2many('account.payment.fast.line','fast_payment',string="Líneas Pago Rápido")
    payment_ids = fields.One2many('account.payment','account_payment_fast',string="Pagos Creados")
    payment_count = fields.Integer("Cantidad de Pagos", compute='_compute_payment_count')
    total_cash_usd = fields.Float(string="Total Efectivo USD",compute="_compute_total",store=True)
    total_cash_bs  = fields.Float(string="Total Efectivo VED",compute="_compute_total",store=True)
    total_bank_usd = fields.Float(string="Total Banco USD",compute="_compute_total",store=True)
    total_bank_bs = fields.Float(string="Total Banco VED",compute="_compute_total",store=True)
    

    @api.depends('order_line','order_line.amount','order_line.amount_bs')
    def _compute_total(self):
        for rec in self:
            rec.total_cash_usd = sum(rec.order_line.filtered(lambda x: x.journal_id.type =='cash' and not x.currency_id).mapped('amount'))
            rec.total_cash_bs = sum(rec.order_line.filtered(lambda x: x.journal_id.type =='cash' and x.journal_id.currency_id.name in ('VED','VEF','VES')).mapped('amount_bs'))
            rec.total_bank_usd = sum(rec.order_line.filtered(lambda x: x.journal_id.type =='bank' and not x.currency_id).mapped('amount'))
            rec.total_bank_bs = sum(rec.order_line.filtered(lambda x: x.journal_id.type =='bank' and x.journal_id.currency_id.name in ('VED','VEF','VES')).mapped('amount_bs'))

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)

    def cancelar(self):
        for rec in self:
            rec.state='cancel'

    def confirmar(self):
        for rec in self:
            if rec.name == '/':
                rec.name = self.env['ir.sequence'].next_by_code('account.payment.fast')
            rec.state='done'
            rec.confirmed_by = self.env.user.id


    def crear_pagos(self):
        for rec in self:
            for line in rec.order_line:
                if line.rate <= 0:
                    raise UserError(('La tasa de la línea %s, debe ser mayor que cero')%(line.name))
                line.payment_id = self.env['account.payment'].create(line.payment_dict()).id
            rec.confirmed_by = self.env.user.id
            rec.state='payment'

    def open_payments(self):
        self.ensure_one()
        res = self.env.ref('account.action_account_payments')
        res = res.read()[0]
        res['domain'] = str([('account_payment_fast', '=', self.id)])
        res['context'] = {'create':False,'delete':False}
        return res

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft','cancel') or rec.name != '/':
                raise UserError('No puede borrar un Pago Rápido que haya estado confirmado')
        return super().unlink()