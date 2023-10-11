# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import base64
from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class RelacionPagoWizardCierre(models.TransientModel):
    _name = 'relacion.pagos.wizard.cierre'

    date = fields.Date('Fecha', required=True)
    user_id = fields.Many2many('res.users',string="Vendedor",help="Este campo puede estar vacío, de estarlo, buscará todo los vendedores que tengan venta ese día")
    payment_type = fields.Selection([('outbound', 'Pagos'), ('inbound', 'Cobros'),('all', 'Todos')], required = True, default='outbound', string="Tipo")
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        string="Compañia",
        readonly=True,
    )
    partner_id = fields.Many2one('res.partner','Contacto')
    tipo_de_reporte =  fields.Selection([
        ("grande", 'Grande'),
        ("pequeno", 'Pequeño'),
        ], string="Tipo de Reporte",default='grande')

    def compute_abono(self):
        for rec in self:
            line_ids = self.env["account.move.line"] \
                .search([]) \
                .filtered(lambda l: all([
                    l.company_id == rec.company_id,
                    l.move_id.partner_id == rec.partner_id,
                    l.account_id.user_type_id.type in ('receivable'),
                    l.move_id.state == 'posted',
                ]))
            
            abono = 0

            for line in line_ids:
                if line.currency_id == self.env.company.currency_id:
                    abono += line.amount_currency / line.move_id.manual_currency_exchange_rate
                else:
                    abono += line.amount_currency

            abono = abs(abono) if abono < 0 else 0
            return abono
    def get_data(self):
        pagos = []
        user_list = []
        journal_list = {}
        domain = [('date','=',self.date),('state','=','posted')]
        if self.user_id:
            domain += [('create_uid', 'in', self.user_id.ids)]
        if self.partner_id:
            domain += [('partner_id', '=', self.partner_id.id)]
        if self.payment_type == 'outbound':
            domain += [('payment_type', '=', self.payment_type)]
        if self.payment_type == 'inbound':
            domain += [('payment_type', '=', self.payment_type)]

        payment_ids = self.env['account.payment'].search(domain)
        user_id = payment_ids.mapped('create_uid')
        journal_id = payment_ids.mapped('journal_id')

        if not payment_ids:
            raise UserError('No se encontraron registros')
        pagos_diarios = []
        diarios_y_totales=[]
        for journal in journal_id:

            diarios_y_totales.append({'journal_name': journal.name,
                                     'journal_total_amount':(sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id and x.currency_id == self.env.company.currency_id).mapped('amount')) + sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id and x.currency_id != self.env.company.currency_id).mapped('amount_ref'))) - (sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id and x.currency_id == self.env.company.currency_id).mapped('amount')) + sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id and x.currency_id != self.env.company.currency_id).mapped('amount_ref'))),
                                     'journal_total_amount_ref':(sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id and x.currency_id != self.env.company.currency_id).mapped('amount')) + sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id and x.currency_id == self.env.company.currency_id).mapped('amount_ref'))) - (sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id and x.currency_id != self.env.company.currency_id).mapped('amount')) + sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id and x.currency_id == self.env.company.currency_id).mapped('amount_ref'))),
                                     #'journal_total_amount_ref':sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id).mapped('amount')) - sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id).mapped('amount_ref')),
})
        for user in user_id:
            mis_diarios = []
            for journal in journal_id:
                journal_vals = {
                        'journal_name': journal.name,
                        'journal_currency': journal.currency_id,
                        'journal_id': journal.id,
                        'journal_total_amount':sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id).mapped('amount')) - sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id).mapped('amount')),
                        'journal_total_amount_ref':sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and  x.journal_id.id == journal.id).mapped('amount')) - sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and  x.journal_id.id == journal.id).mapped('amount')),
                        'journal_amount': sum(payment_ids.filtered(lambda x: x.payment_type == 'inbound' and x.create_uid.id == user.id and x.journal_id.id == journal.id).mapped('amount')) - sum(payment_ids.filtered(lambda x: x.payment_type == 'outbound' and x.create_uid.id == user.id and x.journal_id.id == journal.id).mapped('amount')),
                        'journal_lines':[],
                    }
                for p in payment_ids.filtered(lambda x: x.create_uid.id == user.id and x.journal_id.id == journal.id):
                    monto_total = 0
                    monto_total_ref = 0
                    if p.payment_type == 'inbound':
                        monto_total = p.amount if p.currency_id == self.env.company.currency_id else p.amount_ref
                        monto_total_ref = p.amount if p.currency_id != self.env.company.currency_id else p.amount_ref
                    else:
                        monto_total = -p.amount if p.currency_id == self.env.company.currency_id else -p.amount_ref
                        monto_total_ref = -p.amount if p.currency_id != self.env.company.currency_id else -p.amount_ref

                    journal_vals['journal_lines'].append({
                        'id':p.id,
                        'tipo_pago': 'Cobros' if p.payment_type == 'inbound' else 'Pagos',
                        'name':p.name,
                        'ref':p.ref,
                        'journal_name':p.journal_id.name,
                        'journal_id':p.journal_id.id,
                        'journal_type':p.journal_id.type,
                        'proveedor':p.partner_id.name,
                        'productor':p.productor.name,
                        'autorizado':p.autorizado.name,
                        'monto_total':round(monto_total,2),
                        'monto_total_ref':round(monto_total_ref,2),
                        'moneda':p.currency_id.symbol,
                        'fecha_pago':p.date,
                        'pago_id':p.move_id.id,
                        'create_uid':p.create_uid.name,
                        #'acciones': [rec[2].move_id.accion_id.name for rec in p.move_id._get_reconciled_invoices_partials()],
                        'facturas': [rec[2].move_id.name for rec in p.move_id._get_reconciled_invoices_partials()],
                        'count_move_id':int(len(p.move_id._get_reconciled_invoices_partials())),
                        'es_igtf': p.is_igtf_payment,
                        #'accion_id':p.accion_id.name,
                        })
                    pagos_diarios.append({
                        'id':p.id,
                        'tipo_pago': 'Cobros' if p.payment_type == 'inbound' else 'Pagos',
                        'name':p.name,
                        'ref':p.ref,
                        'journal_name':p.journal_id.name,
                        'journal_id':p.journal_id.id,
                        'journal_type':p.journal_id.type,
                        'proveedor':p.partner_id.name,
                        'productor':p.productor.name,
                        'autorizado':p.autorizado.name,
                        'monto_total':round(monto_total,2),
                        'monto_total_ref':round(monto_total_ref,2),
                        'moneda':p.currency_id.symbol,
                        'fecha_pago':p.date,
                        'pago_id':p.move_id.id,
                        'create_uid':p.create_uid.name,
                        #'acciones': [rec[2].move_id.accion_id.name for rec in p.move_id._get_reconciled_invoices_partials()],
                        'facturas': [rec[2].move_id.name for rec in p.move_id._get_reconciled_invoices_partials()],
                        'count_move_id':int(len(p.move_id._get_reconciled_invoices_partials())),
                        'es_igtf': p.is_igtf_payment,
                        #'accion_id':p.accion_id.name,
                        })
                mis_diarios.append(journal_vals)
            user_list.append({
                'user': user.name,
                'user_id': user.id,
                'lineas':mis_diarios,
            })
        data = {
            'cabecera': user_list,
            'diarios':diarios_y_totales,
            'payment_type': 'Cobros' if self.payment_type == 'inbound' else 'Pagos' if self.payment_type == 'outbound' else 'Todos',
            'fecha':  self.date,
            'partner_id_obj_name':  self.partner_id.name,
            'company_id_obj_name':  self.company_id.name,
            'company_id_obj_rif':  self.company_id.rif,
            'company_id_obj_logo':  self.company_id.logo,
            'company_id_obj_street': self.company_id.street+' '+self.company_id.city,
            'user_id_obj_name':  self.env.user.name,
            'solo_pagos': pagos_diarios,
            'bono_o_deuda':self.compute_abono()
        }
        
        return data


    def reporte_relacion_pago(self):

        data=self.get_data()
        if self.tipo_de_reporte == 'grande':
            return self.env.ref('eu_reporte_cierre_diario.relacion_pagos_report_cierre').report_action(self, data=data)
        else:
            return self.env.ref('eu_reporte_cierre_diario.relacion_pagos_template_peq_action').report_action(self, data=data)



        
    def send_email_with_attachment(self):

        data=self.get_data()
        if self.tipo_de_reporte == 'grande':
            report_template_id = self.env.ref(
            'eu_reporte_cierre_diario.relacion_pagos_report_cierre')._render_qweb_pdf(self, data=data)
        else:
            report_template_id = self.env.ref(
            'eu_reporte_cierre_diario.relacion_pagos_template_peq_action')._render_qweb_pdf(self, data=data)

        
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': f"Relacion_{self.partner_id.name}.pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        template = self.env.ref(
            'eu_reporte_cierre_diario.reporte_relacion_usurio_email_template')
        template.attachment_ids = [(6, 0, [data_id.id])]
        email_values = {'email_to': self.partner_id.email,
                        'email_from': self.env.user.email}
        template.send_mail(self.id, email_values=email_values, force_send=True)
        template.attachment_ids = [(3, data_id.id)]
        return True



class ParticularReport(models.AbstractModel):
    _name = 'report.eu_report_cierre_diario.relacion_pagos_template_cierre'

    def _get_report_values(self, docids, data=None):
        # get the report action back as we will need its data
        
        # return a custom rendering context
        return {
            'doc_ids':data.get("doc_ids"),
            'doc_model': "relacion.pagos.wizard.cierre",
            'docs':docids,
            'datas':data

        }


class ParticularReportV(models.AbstractModel):
    _name = 'report.eu_report_cierre_diario.relacion_pagos_template_peq'

    def _get_report_values(self, docids, data=None):
        # get the report action back as we will need its data
        
        # return a custom rendering context
        return {
            'doc_ids':data.get("doc_ids"),
            'doc_model': "relacion.pagos.wizard.cierre",
            'docs':docids,
            'datas':data

        }
        