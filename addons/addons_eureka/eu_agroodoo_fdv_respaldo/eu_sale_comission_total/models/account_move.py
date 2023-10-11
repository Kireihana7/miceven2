# -*- coding: utf-8 -*-
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("commission_id",'amount_untaxed','amount_total')
    def _compute_commission_total(self):
        for rec in self:
            rec.commission_total = 0
            rec.commission_percent = 0
            if rec.commission_id and rec.commission_id.amount_base_type == 'base_imponible':
                rec.commission_total,rec.commission_percent =  rec.commission_id.calculate_section(rec.amount_untaxed)
            elif rec.commission_id and rec.commission_id.amount_base_type == 'monto_total':
                rec.commission_total,rec.commission_percent = rec.commission_id.calculate_section(rec.amount_total)

    commission_total = fields.Float(
        string="Monto Comisión",
        compute="_compute_commission_total",
        store=True,
        copy=False
    )
    commission_percent = fields.Float(
        string="Porcentaje Comisión",
        compute="_compute_commission_total",
        store=True,
        copy=False)

    comission_partner = fields.Many2one(
        string="Comisionista",
        comodel_name="res.partner",
        compute="_compute_comission_partner",
        copy=False
    )

    @api.depends("invoice_user_id")
    def _compute_comission_partner(self):
        for rec in self:
            rec.comission_partner = self.env['res.partner'].search([('user_comission','=',rec.invoice_user_id.id)],limit=1).id or False

    @api.depends("comission_partner","company_id","move_type")
    def _compute_commission_id(self):
        for rec in self:
            if rec.move_type in ('out_invoice','out_refund'):
                rec.commission_id = self.env['sale.commission'].search([
                    ('partner_id','=',rec.comission_partner.id),
                    ('company_id','=',rec.company_id.id),
                    ('state','=','active'),
                    ('ejecutar','=','invoice'),
                    ],limit=1).id or False
            else:
                rec.commission_id = False

    commission_id = fields.Many2one(
        comodel_name="sale.commission",
        ondelete="restrict",
        compute="_compute_commission_id",
        store=True,
        readonly=True,
        copy=False,
    )
    commission_id_full = fields.Many2one(
        comodel_name="sale.commission.full",
        readonly=True,
        copy=False,
    )
    commission_id_line = fields.Many2one(
        comodel_name="sale.commission.line",
        readonly=True,
        copy=False,
        string="Línea de Comisión",
    )
    commission_payment_id = fields.Many2one('sale.commission',string="Comisión de Pago Vinculada",readonly=True)
    commission_payment_id_line = fields.Many2one('sale.commission.line',string="Línea de Pägo Comisión",readonly=True)
    commission_payment_id_payment = fields.Many2one('sale.commission.payment',string="Pago de Comisión",readonly=True)

    def button_draft(self):
        for rec in self:
            if rec.commission_payment_id_payment:
                raise UserError('No puedes Cancelar una factura de Comisiones. Realice una Nota de Crédito.')
            if rec.commission_id_full:
                raise UserError('No puedes Cancelar una factura de Comisiones. Realice una Nota de Crédito desde el lote.')

    def button_cancel(self):
        for rec in self:
            if rec.commission_payment_id_payment:
                raise UserError('No puedes Cancelar una factura de Comisiones. Realice una Nota de Crédito.')
            if rec.commission_id_full:
                raise UserError('No puedes Cancelar una factura de Comisiones. Realice una Nota de Crédito desde el lote.')

    def action_reverse(self):
        for rec in self:
            if rec.commission_payment_id_payment:
                raise UserError('Realice la Nota de Crédito a través de la Línea de Comisión.')
            if rec.commission_id_full:
                raise UserError('Realice la Nota de Crédito a través del Lote de Comisión.')

    def action_post(self):
        for rec in self:
            if rec.commission_id and rec.commission_id.state != 'active' and not rec.commission_id_line:
                rec._compute_commission_id()
                rec._compute_commission_total()
            if rec.commission_id and rec.commission_id.state == 'active' and not rec.commission_id_line:
                data = {
                    'commission_id': rec.commission_id.id,
                    'sale_id': False,
                    'invoice_id': rec.id,
                    'partner_id': rec.partner_id.id,
                    'amount_total': rec.commission_total,
                    'amount_to_paid': rec.commission_total,
                    'amount_paid': rec.commission_total,
                    'payment_state': 'not_paid',
                }
                lines = self.env['sale.commission.line'].sudo().create(data)
                rec.commission_id_line = lines.id
        res = super(AccountMove, self).action_post()

    def write(self,vals):
        for rec in self:
            if vals.get('state')  != 'posted' and rec.commission_id_line and rec.commission_id_line.amount_total != rec.commission_id_line.amount_to_paid:
                raise UserError('No puedes modificar una Factura que tenga una comision pagada')
        res = super(AccountMove, self).write(vals)
        for rec in self:
            if rec.commission_id_line and rec.commission_id_line.amount_total == rec.commission_id_line.amount_to_paid:
                data = {
                    'commission_id': rec.commission_id.id,
                    'name': '%s - %s' % (rec.name,rec.partner_id.name) ,
                    'sale_id': False,
                    'invoice_id': rec.id,
                    'partner_id': rec.partner_id.id,
                    'amount_total': rec.commission_total,
                    'amount_to_paid': rec.commission_total,
                    'amount_paid': 0,
                    'payment_state': 'not_paid',
                }
                rec.commission_id_line.sudo().write(data)
            if rec.commission_id_line and (rec.commission_id_line.amount_total != rec.commission_id_line.amount_to_paid or rec.commission_id_line.payment_state != 'not_paid') and rec.commission_id_line.amount_total != rec.commission_total:
                raise UserError('No puedes modificar el monto de una Factura que ya tenga comisión pagada')
        return res