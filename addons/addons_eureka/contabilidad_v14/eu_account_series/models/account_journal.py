# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    multi_serie     =   fields.Boolean(string="Multiserie company",invisible=True, related="company_id.multi_serie")
    account_serie   =   fields.Many2one('account.tipo.serie',string="Tipo de Serie")
    nota_entrega 	= 	fields.Boolean(string="Diario para Nota de Entrega",default=False)