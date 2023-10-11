#coding: utf-8

from odoo import fields, models

class res_company(models.Model):
    """
    Override to add check lists
    """
    _inherit = "res.company"

    check_line_ids_account = fields.One2many(
        "account.check.item",
        "company_id",
        string="Listas de verificación",
        copy=True,
    )
    no_stages_ids_account = fields.One2many(
        "account.check.item",
        "company_no_id",
        string="""Determine los estados, cuya transferencia no requiere completar las listas de verificación en la actualidad
         etapa""",
        copy=True,
    )
