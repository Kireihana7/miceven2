from datetime import datetime, timedelta,date
from odoo import models, fields,api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class NominaGlobalWizardUSD(models.TransientModel):
    _inherit = 'nomina.global.wizard'

    currency_id = fields.Many2one("res.currency", string="Moneda",default=lambda self: self.env.company.currency_id.parent_id)
