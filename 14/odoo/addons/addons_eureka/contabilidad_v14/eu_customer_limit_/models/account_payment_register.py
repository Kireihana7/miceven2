# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    banco_origen =  fields.Selection([
        ("0102", 'Banco de Venezuela S.A.C.A. Banco Universal'),
        ("0104", 'Venezolano de Crédito, S.A. Banco Universal'),
        ("0105", 'Banco Mercantil, C.A S.A.C.A. Banco Universal'),
        ("0108", 'Banco Provincial, S.A. Banco Universal'),
        ("0114", 'Bancaribe C.A. Banco Universal'),
        ("0115", 'Banco Exterior C.A. Banco Universal'),
        ("0116", 'Banco Occidental de Descuento, Banco Universal C.A.'),
        ("0128", 'Banco Caroní C.A. Banco Universal'),
        ("0134", 'Banesco Banco Universal S.A.C.A.'),
        ("0137", 'Banco Sofitasa Banco Universal'),
        ("0138", 'Banco Plaza Banco Universal'),
        ("0146", 'Banco de la Gente Emprendedora C.A.'),
        ("0149", 'Banco del Pueblo Soberano, C.A. Banco de Desarrollo'),
        ("0151", 'BFC Banco Fondo Común C.A Banco Universal'),
        ("0156", '100% Banco, Banco Universal C.A.'),
        ("0157", 'DelSur Banco Universal, C.A.'),
        ("0163", 'Banco del Tesoro, C.A. Banco Universal'),
        ("0166", 'Banco Agrícola de Venezuela, C.A. Banco Universal'),
        ("0168", 'Bancrecer, S.A. Banco Microfinanciero'),
        ("0169", 'Mi Banco Banco Microfinanciero C.A.'),
        ("0171", 'Banco Activo, C.A. Banco Universal'),
        ("0172", 'Bancamiga Banco Microfinanciero C.A.'),
        ("0173", 'Banco Internacional de Desarrollo, C.A. Banco Universal'),
        ("0174", 'Banplus Banco Universal, C.A.'),
        ("0175", 'Banco Bicentenario Banco Universal C.A.'),
        ("0176", 'Banco Espirito Santo, S.A. Sucursal Venezuela B.U.'),
        ("0177", 'Banco de la Fuerza Armada Nacional Bolivariana, B.U.'),
        ("0190", 'Citibank N.A.'),
        ("0191", 'Banco Nacional de Crédito, C.A. Banco Universal'),
        ("0601", 'Instituto Municipal de Crédito Popular'),
        ], string="Banco Origen")


    def _create_payment_vals_from_wizard(self):
        result = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        result.update({
            'banco_origen':self.banco_origen,
        })
        return result

    @api.model
    def default_get(self, fields):
        result = super(AccountPaymentRegister, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'account.move':
            return result
        move_id = self.env['account.move'].browse(self._context.get('active_ids')).filtered(lambda move: move.is_invoice(include_receipts=True))
        result.update({
            'partner_bank_id':move_id[0].partner_bank_id.id,
            })
        return result