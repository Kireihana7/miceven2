# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner Activate'

    state = fields.Selection(
        [('inactivo', 'Inactivo'), ('activo', 'Activo'), ],
        string='State', default='inactivo', track_visibility='always')

    def action_desactivate(self):
        self.write({'state': 'inactivo'})
        return True

    def action_activate(self):
        self.write({'state': 'activo'})
        return True
        
    def write(self,vals):
        for rec in self:
            if (self._context.get('active_model')=="res.partner" and rec.state == 'activo' and not vals.get('state') and not vals.get('property_stock_customer') and not vals.get('property_stock_supplier') and not vals.get('rif'))  :
                raise UserError('No puedes modificar un contacto Activo')
            if rec.state == 'activo' and vals.get('state'):
                res = super(ResPartner,self).write(vals)
            if rec.state=='inactivo':
                res = super(ResPartner,self).write(vals)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_state = fields.Selection(related='partner_id.state')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_state = fields.Selection(related='partner_id.state')
