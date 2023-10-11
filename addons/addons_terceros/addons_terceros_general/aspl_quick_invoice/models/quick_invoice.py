# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _

import ast


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        quick_invoice_journal_ids = self.env['ir.config_parameter'].sudo().get_param('quick_invoice_journal_ids')
        if quick_invoice_journal_ids:
            res.update({'quick_invoice_journal_ids':ast.literal_eval(quick_invoice_journal_ids)})
        return res

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('quick_invoice_journal_ids', self.quick_invoice_journal_ids.ids)
        return res

    quick_invoice_journal_ids = fields.Many2many('account.journal', string='Journal')
    quick_invoice_warehouse_id = fields.Many2one(
        "stock.warehouse", 
        "Almacen de venta rápida",
        config_parameter="aspl_quick_invoice.quick_invoice_warehouse_id",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
