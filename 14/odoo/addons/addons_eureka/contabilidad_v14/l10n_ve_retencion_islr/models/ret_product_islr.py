# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RetProductIslr(models.Model):
    _inherit = 'product.template'

    service_concept_retention = fields.Many2one('account.withholding.concept', 'Withholding', copy=False)


