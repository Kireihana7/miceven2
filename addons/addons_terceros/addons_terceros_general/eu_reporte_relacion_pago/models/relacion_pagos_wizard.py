# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class RelacionPagoWizard(models.TransientModel):
    _name = 'relacion.pagos.wizard'

    date_start = fields.Date('Fecha Inicio', required=True)
    date_end = fields.Date('Fecha Fin', required=True)
    partner_id = fields.Many2one('res.partner', string='Proveedor / Cliente', required = True)

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        string="Compañia",
        readonly=True,
    )

    payment_type = fields.Selection([('outbound', 'Pagos'), ('inbound', 'Cobros')], required = True, default='outbound', string="Tipo")
    
    payment_ids = fields.Many2many(
        'account.payment',
        string='Pagos / Cobros',
        domain = "[('partner_id', '=', partner_id),('payment_type', '=', payment_type),('date', '>=', date_start),('date', '<=', date_end),('state', '=', 'posted')]",
        required = True
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.payment_type = False
        self.payment_ids =  False

    @api.onchange('payment_type')
    def onchange_payment_type(self):
        self.payment_ids =  False

    def reporte_relacion_pago(self):

        final = []
        #lineas = []
        pagos = []
        # anticipo = []

        for p in self.payment_ids:
            pagos.append(p.id)
            for pa in self.env['account.payment'].search([('id', '=', p.id)]):
                lineas = []
                # if pa.free_payment:
                #     for hijos in self.env['account.move'].search([('payment_id', '=', p.id),('id','!=',p.move_id.id),('move_type','=','entry')]):
                #         for fc in hijos._get_reconciled_invoices_partials():
                #             amount_two = fc[1]
                #             inv_two = fc[2].move_id
                #             if inv_two.move_type != 'entry':
                #                 anticipo.append({
                #                         'fecha_factura':inv_two.invoice_date,
                #                         'numero_factura': inv_two.name,
                #                         'referencia':pa.name,
                #                         'monto_factura':float(inv_two.amount_total),
                #                         'pagado':amount_two,
                #                         'balance':inv_two.amount_residual,
                #                         'currency_id':inv_two.currency_id.id,
                #                         'move_id': p.move_id.id,
                #                     })
                #             #raise UserError(pa.move_id.id)
                for rec in pa.move_id._get_reconciled_invoices_partials():
                    #raise UserError(rec)
                    amount = rec[1]
                    inv = rec[2].move_id
                    if inv.move_type != 'entry':
                        lineas.append({
                            'fecha_factura':inv.invoice_date,
                            'numero_factura': inv.name,
                            'nombre':pa.name,
                            'referencia':pa.ref,
                            'referencia_dos':pa.ref_bank,
                            'monto_factura':float(inv.amount_total),
                            'pagado':amount,
                            'balance':inv.amount_residual,
                            'currency_id':inv.currency_id.id,
                            'move_id': p.move_id.id,
                        })
                
                final.append({
                    'id':pa.id,
                    'tipo_pago':pa.payment_type,
                    'name':pa.name,
                    'proveedor':pa.partner_id.name,
                    'monto_total':pa.amount,
                    'monto_total_ref':pa.amount_ref,
                    'moneda':pa.currency_id.symbol,
                    'moneda_ref':pa.currency_id_ref.symbol,
                    'fecha_pago':pa.date,
                    'pago_id':pa.move_id.id,
                    'lineas': lineas,
                    'referencia':pa.ref,
                    'referencia_dos':pa.ref_bank,
                    #'anticipo':anticipo,
                    'count_move_id':int(len(pa.move_id._get_reconciled_invoices_partials())),
                    })
        data = {
            'cabecera': final,
            'payment_type': 'Cobros' if self.payment_type == 'inbound' else 'Pagos',
            'desde':  self.date_start if self.date_start else '',
            'hasta':  self.date_end if self.date_end else '',
            'pagos': pagos,
            'partner_id': self.partner_id.rif+' '+self.partner_id.name if self.partner_id else '',
        }

        return self.env.ref('eu_reporte_relacion_pago.relacion_pagos_report').report_action(self, data=data)