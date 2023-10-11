from odoo import models, api,fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    fiscal_id = fields.Many2one('fiscal.book', 'Libro Fiscal')
    issue_fiscal_id = fields.Many2one('fiscal.book', 'Facturas Problematicas')