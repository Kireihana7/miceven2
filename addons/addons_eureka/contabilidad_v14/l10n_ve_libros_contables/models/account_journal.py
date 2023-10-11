from odoo import models, api,fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_fiscal = fields.Boolean(string="A declarar")
