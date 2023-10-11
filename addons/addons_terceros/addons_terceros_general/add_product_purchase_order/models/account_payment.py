from odoo import models, fields,api,_
from odoo.exceptions import UserError
from odoo.osv import expression

class AccountPayment(models.Model):
    _inherit = "account.payment"

    productor = fields.Many2one('res.partner',string="Productor")