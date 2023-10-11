# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AcuerdoLiquidacion(models.Model):
    _name = "acuerdo.liquidacion"
    _description = "Acuerdo liquidación"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nombre", tracking=True,)
    payment_ids = fields.One2many("account.payment", "acuerdo_liquidacion_id", "Pagos", tracking=True,)
    currency_id = fields.Many2one("res.currency", "Moneda", tracking=True, default=lambda self: self.env.company.currency_id)
    ref_currency_id = fields.Many2one("res.currency", "Moneda de referencia", tracking=True)
    amount_total = fields.Monetary("Monto total", compute="_compute_amounts", tracking=True,)
    amount_ref_total = fields.Monetary(
        "Monto de referencia",
        currency_field="ref_currency_id",
        compute="_compute_amounts",
        tracking=True,
    )
    weight_total = fields.Float("Peso total", compute="_compute_weight_total", tracking=True,)
    average_price = fields.Monetary("Precio unitario", compute="_compute_average_price", tracking=True)
    partner_id = fields.Many2one("res.partner", "Proveedor", tracking=True,)
    agreement_date = fields.Date("Fecha de acuerdo", tracking=True,)
    due_date = fields.Date("Fecha de cúlmen", tracking=True,)
    product_id = fields.Many2one("product.product", "Producto", tracking=True,)
    reception_quantity = fields.Float("Cantidad acordada a recibir", tracking=True)
    state = fields.Selection([
        ("borrador", "Borrador"),
        ("anticipo", "Anticipo"),
        ("liquidando", "Liquidando"),
        ("liquidado", "Liquidado"),
        ("cancelado", "Cancelada"),
    ], "Estatus de liquidación", compute="_compute_state", tracking=True, store=True)
    is_confirmed = fields.Boolean()
    is_cancelled = fields.Boolean()
    purchase_order_ids = fields.One2many("purchase.order", "liquidacion_id", "PO", tracking=True)
    invoice_ids = fields.Many2many(
        "account.move", 
        "invoice_liquidacion_rel", 
        "liquidacion_id",
        "invoice_id",
        "Facturas",
        compute="_compute_invoice_ids",
        tracking=True,
    )
    chargue_consolidate_ids = fields.One2many("chargue.consolidate", "liquidacion_id", "ODD / ODC", tracking=True)

    def action_confirm(self):
        for rec in self:
            rec.is_confirmed = True

    def action_cancel(self):
        for rec in self:
            if rec.state in ["liquidando", "liquidado"]:
                raise UserError("No se puede cancelar un acuerdo que esté en " + rec.state)

            rec.is_cancelled = True

    def action_create_chargue_consolidate(self):
        return {
            "name": "Romana",
            "type": "ir.actions.act_window",
            "res_model": "chargue.consolidate",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_liquidacion_id": self.id,
                "default_operation_type": "compra",
                "default_partner_id": self.partner_id.id,
                "default_product_id": self.product_id.id,
            },
        }

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        for rec in res:
            rec.name = self.env["ir.sequence"].next_by_code("acuedo.liquidacion.sequence")

        return res

    def unlink(self):
        if any(rec.state != "borrador" for rec in self):
            raise UserError("No puedes borrar una liquidación que no esté en borrador")

        return super().unlink()

    @api.constrains("partner_id", "state")
    def _check_state_and_partner_id(self):
        for rec in self:
            if self.search([("state","in",["anticipo","liquidando"]),("partner_id","=",rec.partner_id.id),("id","!=",rec.id)],limit=1):
                raise ValidationError("Ya hay una liquidación activa con ese cliente")

    @api.depends("weight_total", "amount_total")
    def _compute_average_price(self):
        for rec in self:
            rec.average_price = round(rec.amount_total / (rec.weight_total or 1), 4)

    @api.depends(
        "payment_ids.debit_partial_reconcile_ids.debit_move_parent_id",
        "payment_ids.credit_partial_reconcile_ids.credit_move_parent_id",
        "payment_ids.debit_partial_reconcile_ids.debit_move_parent_id",
        "payment_ids.credit_partial_reconcile_ids.credit_move_parent_id",
        "purchase_order_ids.order_line.invoice_lines.move_id",
    )
    def _compute_invoice_ids(self):
        for rec in self:
            reconcile = rec.payment_ids.debit_partial_reconcile_ids + rec.payment_ids.credit_partial_reconcile_ids

            ids = rec.purchase_order_ids.order_line.invoice_lines.move_id.ids
            ids += reconcile.debit_move_parent_id.ids
            ids += reconcile.credit_move_parent_id.ids

            rec.invoice_ids = ids

    @api.depends(
        "payment_ids.importe_na",
        "payment_ids.currency_id",
        "payment_ids.amount_ref",
        "payment_ids.amount",
        "currency_id",
        "is_confirmed",
        "is_cancelled",
    )
    def _compute_state(self):
        for rec in self:
            if not rec.is_confirmed:
                rec.state = "borrador"
            elif rec.is_cancelled:
                rec.state = "cancelado"
            elif not rec.payment_ids:
                rec.state = "anticipo" 
            elif all(importe <= 0 for importe in rec.payment_ids.mapped("importe_na")):
                rec.state = "liquidado"
            elif any(payment.importe_na != (payment.amount if payment.currency_id == rec.currency_id else payment.amount_ref)  for payment in rec.payment_ids):
                rec.state = "liquidando"
            else:
                rec.state = "anticipo"
        
    @api.depends(
        "currency_id",
        "ref_currency_id",
        "payment_ids.state",
        "payment_ids.amount", 
        "payment_ids.amount_ref", 
        "payment_ids.currency_id", 
        "payment_ids.currency_id_ref",
    )
    def _compute_amounts(self):
        for rec in self:
            rec.amount_total = rec.amount_ref_total = 0

            for payment in rec.payment_ids.filtered_domain([("state", "=", "posted")]):
                if rec.currency_id == payment.currency_id:
                    rec.amount_total += payment.amount
                elif rec.currency_id == payment.currency_id_ref:
                    rec.amount_total += payment.amount_ref

                if rec.ref_currency_id == payment.currency_id:
                    rec.amount_ref_total += payment.amount
                elif rec.ref_currency_id == payment.currency_id_ref:
                    rec.amount_ref_total += payment.amount_ref
        
    @api.depends("payment_ids.weight", "payment_ids.state")
    def _compute_weight_total(self):
        for rec in self:
            rec.weight_total = sum(rec
                .payment_ids
                .filtered(lambda p: p.state == "posted")
                .mapped("weight")
        )
        