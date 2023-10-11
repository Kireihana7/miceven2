# -*- coding: utf-8 -*-

from datetime import date
from odoo import _, api, fields, models

class ResPartnerAutorizados(models.Model):
    _name = 'res.partner.autorizados'
    _description = 'Autorizados para Pagos'

    partner_id = fields.Many2one('res.partner','Contacto')
    autorizados = fields.Many2one('res.partner','Autorizado',domain="[('id','!=',id)]")
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company,string="Compañia",readonly=True)
    name = fields.Char(related="autorizados.name")
    bank_ids = fields.One2many(related="autorizados.bank_ids")


