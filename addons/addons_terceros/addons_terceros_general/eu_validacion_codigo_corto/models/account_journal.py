# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.constrains('code')
    def _code_unique(self):
        aj = self.env['account.journal'].search_count([('code','=',self.code),('company_id','=',self.env.company.id)])
        if aj > 1:
            raise UserError(_("El Código no se puede repetir por Compañia."))