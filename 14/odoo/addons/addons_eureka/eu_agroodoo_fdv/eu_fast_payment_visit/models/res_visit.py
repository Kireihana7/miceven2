# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResVisit(models.Model):
    _inherit = 'res.visit'

    fast_payment_ids = fields.One2many('account.payment.fast','visit_id',string="Pagos Rápidos")
    fast_payment_ids_count = fields.Integer(string="Pagos Rápidos realizados",compute="_compute_fast_payment_ids_count")

    @api.depends('fast_payment_ids')
    def _compute_fast_payment_ids_count(self):
        for rec in self:
            rec.fast_payment_ids_count = len(rec.fast_payment_ids)

    def open_fast_payment(self):
        self.ensure_one()
        res = self.env.ref('eu_fast_payment.open_account_payment_fast')
        res = res.read()[0]
        res['domain'] = str([('visit_id', '=', self.id)])
        res['context'] = {'delete':False,'default_visit_id':self.id,'viene_de_visita':True,'partner_id':self.partner_id.id}
        return res