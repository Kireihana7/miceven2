# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api,fields,models,_

class AccountInvoice(models.Model):
    _inherit = "account.move"
    
    invoice_cancel_reason_id = fields.Many2one("invoice.cancel.reason", string= "Motivo de cancelación de la factura", help="Este campo muestra el motivo de la cancelación de la factura")
    descripcion = fields.Char(string="Descripción detallada", readonly=True, store=True)
    # action_cancel function return wizard
    def open_wizard_cancel(self,context=None):
        return {
        'name': ('Agregar Motivo'),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'add.invoice.reason',
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target':'new'
    	}
