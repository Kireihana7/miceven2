#coding: utf-8

from odoo import fields, models

class purchase_checklist_history(models.Model):
    """
    A model to keep each change of check list per purchase order
    """
    _name = "purchase.checklist.history"
    _description = "Historial de Verificación"

    check_list_id = fields.Many2one(
        "purchase.check.item",
        string="Verificar item",
    )
    purchase_order_id = fields.Many2one("purchase.order")
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

