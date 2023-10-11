# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'