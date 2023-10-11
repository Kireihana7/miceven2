# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.model
    def _default_warehouse_id(self):
        #res = super(SaleOrder, self)._default_warehouse_id()
        # !!! Any change to the default value may have to be repercuted
        # on _init_column() below.
        return False

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        check_company=True,
        default=_default_warehouse_id,
        )

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            warehouse_id = self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
            self.warehouse_id = False

    @api.onchange('user_id')
    def onchange_user_id(self):
        super().onchange_user_id()
        self.warehouse_id = False