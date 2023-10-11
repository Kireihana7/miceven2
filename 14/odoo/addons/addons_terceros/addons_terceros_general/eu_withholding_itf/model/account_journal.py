# -*- coding: utf-8 -*-


import logging
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tipo_bank = fields.Selection([('na', 'Nacional'),('ex', 'Extranjero')], required=True)
    apply_igft = fields.Boolean(string="¿Aplica IGTF ?",track_visibility="always")
    igtf_percent  = fields.Float(string="Porcentaje de IGTF")
    igtf_account = fields.Many2one('account.account',string="Cuenta para el Pago de IGTF (Clientes)")
    
    @api.constrains
    def constrains_igtf_percent(self):
        for rec in self:
            if rec.igtf_percent > 99 or rec.igtf_percent < 0:
                raise UserError('El porcentaje no puede ser negativo o mayor a 99')