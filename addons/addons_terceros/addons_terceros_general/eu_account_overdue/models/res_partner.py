# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import math
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def view_name_partner(self, cliente):
        cliente_id = self.env['res.partner'].search('id', '=', int(cliente))
        return cliente_id.name