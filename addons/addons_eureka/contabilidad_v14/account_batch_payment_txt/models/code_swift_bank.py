
from odoo import fields, models

class CodeSwiftBank(models.Model):
    _inherit = 'res.partner.bank'

    code_swift = fields.Char('Código Swift', related='bank_id.bic')