#coding: utf-8

from odoo import fields, models

class stock_checklist_history(models.Model):
    """
    A model to keep each change of check list per stock order
    """
    _name = "stock.checklist.history"
    _description = "Historial de Verificación"

    check_list_id = fields.Many2one(
        "stock.check.item",
        string="Verificar item",
    )
    stock_order_id = fields.Many2one("stock.inventory")
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

