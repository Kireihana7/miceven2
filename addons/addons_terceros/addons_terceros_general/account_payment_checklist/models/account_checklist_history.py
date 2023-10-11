#coding: utf-8

from odoo import fields, models

class account_checklist_history(models.Model):
    """
    A model to keep each change of check list per account payment
    """
    _name = "account.checklist.history"
    _description = "Historial de Verificación"

    check_list_id = fields.Many2one(
        "account.check.item",
        string="Verificar item",
    )
    account_payment_id = fields.Many2one("account.payment")
    complete_date = fields.Datetime(
        string="Fecha",
        default=lambda self: fields.Datetime.now(),
    )
    user_id = fields.Many2one(
        "res.users",
        "Usuario",
        default=lambda self: self.env.user.id,
    )
    done_action = fields.Selection(
        (
            ("done", "Realizado"),
            ("reset", "Reset"),
        ),
        string="Acción",
        default="Realizado",
    )

    _order = "complete_date DESC,id"

