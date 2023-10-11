# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial

'''
UPDATE: 07-12-2022: Vista que posiblemente genera este error:    
Fields in 'groupby' must be database-persisted fields (no computed fields) -->
'''
# from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



from werkzeug.urls import url_encode


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agricultural_sale = fields.Boolean(string='Agricultural Sale', default=True)

    analytic_account_id_1 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 0)],
        string='Finca',
        required=True,
        tracking=True
    )

    analytic_account_id_2 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 1)],
        string='Actividad',
        required=True,
        tracking=True
    )        

    analytic_account_id_3 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 2)],
        string='Lote',
        required=False,
        tracking=True
    )

    analytic_account_id_4 = fields.Many2one(
        'account.analytic.account',
        domain=[('num_parents', '=', 3)],
        string='Tablón',
        required=False,
        tracking=True
    )           

    '''
    def action_view_delivery(self):
        super(SaleOrder, self).action_view_delivery()
        if self.order_line:
            raise UserError(_(f'Líneas de productos: {self.order_line}'))    
    '''

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        result = super(SaleOrderLine, self)._prepare_invoice_line()
        result.update({
            'analytic_account_id_1': self.order_id.analytic_account_id_1.id,
            'analytic_account_id_2': self.order_id.analytic_account_id_2.id,
            'analytic_account_id_3': self.order_id.analytic_account_id_3.id,
            'analytic_account_id_4': self.order_id.analytic_account_id_4.id,
        })
        return result
        