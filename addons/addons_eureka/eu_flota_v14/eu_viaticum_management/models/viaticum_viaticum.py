# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    to_viaticum = fields.Boolean("Para viáticos", tracking=True)
    is_reintegro = fields.Boolean("Es reintegro", tracking=True)

    @api.model
    def create(self, vals_list):
        context = self.sudo().env.context

        res = super().create(vals_list)

        for rec in res:
            if rec.is_reintegro and context.get("active_model") == "viaticum.viaticum":
                viaticum = self.env["viaticum.viaticum"].browse(context.get("active_id"))
                viaticum.pago_reintegro_id = rec.id

        return res

    def _check_state_with_viaticum(self):
        for rec in self:
            if rec.state != "posted" and self.env["viaticum.viaticum"].search([("payment_id","=",rec.id)]):
                raise ValidationError("No puedes cancelar el pago si tiene un viático asociado")

    def action_create_viaticum(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Viático',
            'view_mode': 'form',
            "res_model": "viaticum.viaticum",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_payment_id": self.id,
            }
        }

class ViaticumViaticum(models.Model):
    _name = 'viaticum.viaticum'
    _description = 'Viaticos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Código", tracking=True)
    partner_id = fields.Many2one("res.partner", "Cliente", tracking=True)
    payment_id = fields.Many2one("account.payment", "Pago", tracking=True)

    currency_id = fields.Many2one("res.currency", related="payment_id.currency_id", tracking=True)
    amount = fields.Monetary("Monto", related="payment_id.amount", tracking=True)
    balance = fields.Monetary("Balance", compute="_compute_balance", tracking=True)

    currency_id_ref = fields.Many2one("res.currency", related="payment_id.currency_id_ref", tracking=True)
    amount_ref = fields.Monetary(
        "Monto REF", 
        currency_field="currency_id_ref", 
        tracking=True,
        compute="_compute_ref_amounts",
    )
    balance_ref = fields.Monetary(
        "Balance REF", 
        currency_field="currency_id_ref", 
        tracking=True,
        compute="_compute_ref_amounts",
    )
    state = fields.Selection([
        ("draft","Borrador"),
        ("confirm","Confirmada"),
        ("closed", "Cerrada"),
        ("cancel","Cancelada"),
    ], default="draft", string="Estatus", tracking=True)
    invoice_ids = fields.Many2many(
        "account.move",
        "viaticum_move_rel",
        "viaticum_id",
        "move_id",
        "Facturas",
        compute="_compute_invoice_ids",
        tracking=True,
    )
    invoice_count = fields.Integer("Facturas", compute="_compute_invoice_count")
    company_id = fields.Many2one("res.company", "Compañia", default=lambda self: self.env.company)
    pago_reintegro_id = fields.Many2one("account.payment", "Pago de reintegro", tracking=True)
    amount_reintegro = fields.Monetary("Monto de reintegro", compute="_compute_amount_reintegro")
    amount_reintegro_ref = fields.Monetary(
        "Monto de reintegro REF", 
        compute="_compute_amount_reintegro", 
        currency_field="currency_id_ref"
    )

    def action_set_state(self):
        self.write({"state": self._context["state"]})

    @api.depends(
        "currency_id",
        "pago_reintegro_id.amount", 
        "pago_reintegro_id.amount_ref",
        "pago_reintegro_id.currency_id",
    )
    def _compute_amount_reintegro(self):
        for rec in self:
            pago = rec.pago_reintegro_id

            if pago.currency_id == rec.currency_id:
                rec.amount_reintegro = pago.amount
                rec.amount_reintegro_ref = pago.amount_ref
            else:
                rec.amount_reintegro = pago.amount_ref
                rec.amount_reintegro_ref = pago.amount

    @api.depends("invoice_ids")
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)
            
    @api.constrains("payment_id", "partner_id")
    def _check_payment_id(self):
        for rec in self:
            if rec.payment_id.partner_id != rec.partner_id:
                raise ValidationError("El pago no es del mismo cliente")

            if self.search([
                ("id","!=",rec.id),
                ("state","=","confirm"),
                ("payment_id","=",rec.payment_id.id)
            ]):
                raise ValidationError("Ya hay un viático con ese pago asociado")

    @api.constrains("state")
    def _check_state(self):
        for rec in self:
            if rec.state == "confirm" and not rec.payment_id:
                raise ValidationError("No puedes confirmar hasta no haber asociado un pago")
            elif rec.state == "closed" and (not rec.pago_reintegro_id and round(rec.balance,4) > 0):
                raise ValidationError("No puedes cerrar un viático hasta no hacer un pago reintegro")

    @api.depends("payment_id.importe_na", "pago_reintegro_id.amount")
    def _compute_balance(self):
        for rec in self:
            rec.balance = round(rec.payment_id.importe_na - rec.pago_reintegro_id.amount,4)

    @api.depends(
        "payment_id.amount_ref",
        "balance",
        "currency_id_ref",
        "payment_id.manual_currency_exchange_rate",
        "company_id.currency_id",
    )
    def _compute_ref_amounts(self):
        for rec in self:
            pago = rec.payment_id
            rec.amount_ref = rec.payment_id.amount_ref
            rec.balance_ref = round(rec.balance,4)

            if pago.currency_id != self.env.company.currency_id:
                rec.amount_reintegro_ref *= rec.payment_id.manual_currency_exchange_rate
                rec.balance_ref = round(rec.balance / rec.payment_id.manual_currency_exchange_rate,4)


    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        Sequence = self.env["ir.sequence"]
        CODE = "viaticum.sequence"
        COMPANY = self.env.company

        if not Sequence.search([("code", "=", CODE),("company_id", "=", COMPANY.id)]):
            Sequence.create({
                "code": CODE,
                "prefix": "VIAT/",
                'name': f"Viático en {COMPANY.name}",
                'padding': 6,
                'company_id': COMPANY.id,
            })

        for rec in res:
            rec.write({"name": Sequence.next_by_code(CODE)})

        return res

    @api.depends(
        "payment_id.debit_partial_reconcile_ids.debit_move_parent_id",
        "payment_id.credit_partial_reconcile_ids.credit_move_parent_id",
        "payment_id.credit_partial_reconcile_ids.debit_move_parent_id",
        "payment_id.debit_partial_reconcile_ids.credit_move_parent_id",
    )
    def _compute_invoice_ids(self):
        for rec in self:
            payment = rec.payment_id
            reconcile = payment.debit_partial_reconcile_ids + payment.credit_partial_reconcile_ids

            rec.invoice_ids = reconcile.debit_move_parent_id + reconcile.credit_move_parent_id
            rec.invoice_ids = rec.invoice_ids.filtered_domain([('move_type','!=','entry')])

    def action_show_invoices(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Facturas",
            "view_mode": "tree,kanban,form",
            "res_model": "account.move",
            "domain": [("id","in",self.invoice_ids.ids)],
            "context": {
                "create": False,
            },
        }

    def action_create_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas',
            'view_mode': 'form',
            'res_model': 'account.move',
            'context': {
                "default_partner_id": self.partner_id.id,
                "default_move_type": "in_invoice",
                "default_invoice_date": fields.Date.today(),
                "default_currency_id": self.currency_id.id,
            },
        }

    def action_reintegro(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pago de reintegro',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'context': {
                'default_is_reintegro': True,
                'default_move_journal_types': ('bank', 'cash'),
                'default_partner_id': self.partner_id.id,
                'default_payment_type': 'inbound',
                'default_partner_type': 'supplier',
                'default_currency_id': self.currency_id.id,
                'default_amount': self.balance,
                'default_company_id': self.company_id.id,
            },
        }

    def action_viaticum_report(self):
        return self.env \
            .ref("eu_viaticum_management.action_report_viaticum_viatucum") \
            .report_action([], {
                "viaticum_ids": self.ids,
                "currency_id": self.env.ref(f"base.{self.env.context['currency_id']}").id
            })