from odoo import models, api,fields

class AccountwhIvaLine(models.Model):
    _inherit = 'account.wh.iva.line'

    fiscal_id = fields.Many2one('fiscal.book', 'Libro Fiscal')
