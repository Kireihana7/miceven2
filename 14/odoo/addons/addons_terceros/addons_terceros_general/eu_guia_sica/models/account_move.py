from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    guia_sica = fields.Char(string="Guía SICA",tracking=True)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    guia_sica = fields.Char(string="Guía SICA",related="move_id.guia_sica",store=True,tracking=True)