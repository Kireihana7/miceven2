# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    aliquot_type = fields.Selection([('reduced', 'Reduced'),
                                     ('general', 'General'),
                                     ('additional','Additional')],string="Tipo de alicuota", required=False)

class AccountTax(models.Model):
    _inherit = "account.tax"

    aliquot_type = fields.Selection([('reduced', 'Reduced'),
                                     ('general', 'General'),
                                     ('additional','Additional')],string="Tipo de alicuota", required=False)