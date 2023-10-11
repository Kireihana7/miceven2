
# Ford-Ndji Joseph

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

class AccountPaymentWizard(models.TransientModel):
    _name = 'report.account.payment.wizard'
    _description = 'Report account payment'

    desde = fields.Date('Desde', required=True)
    hasta = fields.Date('Hasta', required=True)
    type_report = fields.Selection([
        ('detail_summary', 'Detallado y Resumen'),
        ('only_summary', 'Solo resumen')
    ], string="Tipo de Reporte", required=True)
    currency_id = fields.Many2one('res.currency', String="Moneda a Filtrar")
    report_currency = fields.Selection([
        ('usd', 'Dolár'),
        ('vef', 'Bolívar')
    ], String="Moneda a Reportar", required=True)
    partner_id = fields.Many2many('res.partner', String="Cliente")
    journal_id = fields.Many2many('account.journal', String="Diario")
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company.id,
        copy=True,
        readonly=1,
    )
    # UPDATE: Vendedores
    user_ids = fields.Many2many("res.users", string="Vendedores")


    def print_report(self):
        # Validación de fechas:
        if self.desde > self.hasta:
            raise ValidationError(_('La fecha de inicio no puede ser mayor a la fecha fin.'))            
        domain = [
            ('company_id', '=', self.company_id.id),
            ('payment_reg', '>=', self.desde),
            ('payment_reg', '<=', self.hasta),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('is_internal_transfer', '=', False)
        ]

        if self.currency_id:
            domain.append(('currency_id', '=', self.currency_id.id))
        if self.journal_id:
            domain.append(('journal_id', 'in', self.journal_id.ids))
        if self.partner_id:
            domain.append(('partner_id', 'in', self.partner_id.ids))
        # UPDATE: Vendedores
        if self.user_ids:
            domain.append(('sale_id.user_id', 'in', self.user_ids.ids))

        datas = []
        fechas = []
        journals = []
        payment = self.env["account.payment"].search(domain,order='payment_reg asc')
        fechas.append({
            
            })
        total_amount = 0
        total_amount_ref = 0
        
        # Montos por método de pago:
        efectivo_usd = sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
        efectivo_bs  = sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'cash' and x.currency_id == x.company_id.currency_id).mapped('amount_ref'))
        banco_usd    = sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id == x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id != x.company_id.currency_id).mapped('amount_ref'))
        banco_bs     = sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id != x.company_id.currency_id).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.type == 'bank' and x.currency_id == x.company_id.currency_id).mapped('amount_ref'))

        if not payment:
            raise UserError('No se encontraron registros durante el periodo seleccionado.')

        # ID de las líneas de detalle:
        ids_lineas_detalle = []
        for invoices in payment:
            ids_lineas_detalle.append(invoices.id)
            total_amount += round(invoices.amount,4) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,4)
            total_amount_ref += round(invoices.amount,4) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,4)
            datas.append({
                'date':    str(invoices.payment_reg.strftime("%d/%m/%Y")),
                'payment_id': invoices.name,
                'partner_id': invoices.partner_id.name,
                'journal_id': invoices.journal_id.name,
                'ref':    invoices.ref,
                'amount': round(invoices.amount,4) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,4),
                'currency_id': invoices.currency_id.name,
                'amount_ref': round(invoices.amount,4) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,4),
                'currency_id_ref': invoices.currency_id_ref.name,
            })
        moneda_diario = False
        for journal in payment.mapped('journal_id').sorted(lambda x: x.currency_id):
            moneda_diario = journal.currency_id if journal.currency_id else self.env.company.currency_id
            journals.append({
                'journal_id': journal.name,
                'journal_currency': moneda_diario.symbol,
                'monto_moneda_diario': 0 + sum(payment.filtered(lambda x: x.journal_id.id == journal.id and x.currency_id == moneda_diario).mapped('amount')) + sum(payment.filtered(lambda x: x.journal_id.id == journal.id and x.currency_id != moneda_diario).mapped('amount_ref')),
            })

        # Array de fechas en función a los campos desde y hasta:
        month_list = []
        current_date = self.desde

        while current_date <= self.hasta:
            month_list.append(int(current_date.strftime('%m')))
            current_date += relativedelta(months=1)

            # Detener el bucle si current_date supera la fecha de fin
            if current_date.year == self.hasta.year and current_date.month > self.hasta.month:
                break

        # Añadir meses anteriores al mismo año
        if self.desde.year == self.hasta.year:
            month_list = list(range(1, self.hasta.month + 1))

        # Añadir meses completos de años anteriores
        if self.desde.year < self.hasta.year:
            for year in range(self.desde.year + 1, self.hasta.year):
                month_list = list(range(1, 13)) + month_list
        
        # Agregando nuevos filtros para todas las fechas del año actual:

        domain_all_months_date_effective = [
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.desde),
            ('date', '<=', self.hasta),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('is_internal_transfer', '=', False)
        ]
        payment_all_months_date_effective = self.env["account.payment"].search(domain_all_months_date_effective,order='date asc')

        #  ======================= Inicio de métodos pára la Diferencia ======================= #
        # ID de las líneas de detalle meses:
        ids_lineas_resumen = []
        for invoices in payment_all_months_date_effective:
            ids_lineas_resumen.append(invoices.id)
        
        lista_unida = ids_lineas_detalle + ids_lineas_resumen
        # Eliminando duplicados:
        lista_unida = [elem for elem in lista_unida if lista_unida.count(elem) == 1]

        # Agregando nuevos filtros para todas las fechas del año actual:
        # raise UserError(self.desde.year)
        payment_difference = self.env["account.payment"].search([
            ('company_id', '=', self.company_id.id),
            ('date', '>=', date(self.desde.year, 1, 1)),
            ('date', '<', self.desde),
            ('state', '=', 'posted'),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('is_internal_transfer', '=', False),
            ('id', 'in' , lista_unida)
        ], order='payment_reg asc')

        total_amount_difference = 0
        total_amount_ref_difference = 0
        data_difference = []
        for invoices in payment_difference:
            total_amount_difference += round(invoices.amount,4) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,4)
            total_amount_ref_difference += round(invoices.amount,4) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,4)
            data_difference.append({
                'date':    str(invoices.payment_reg.strftime("%d/%m/%Y")),
                'payment_id': invoices.name,
                'partner_id': invoices.partner_id.name,
                'journal_id': invoices.journal_id.name,
                'ref':    invoices.ref,
                'amount': round(invoices.amount,4) if invoices.currency_id == invoices.company_id.currency_id else round(invoices.amount_ref,4),
                'currency_id': invoices.currency_id.name,
                'amount_ref': round(invoices.amount,4) if invoices.currency_id != invoices.company_id.currency_id else round(invoices.amount_ref,4),
                'currency_id_ref': invoices.currency_id_ref.name,
            })
        #  ======================= Fin de métodos pára la Diferencia ======================= #

        def get_amount_month(report_currency, payment_all_months_date_effective, month):
            amount = 0
            if report_currency == 'usd':
                amount = round(sum(payment_all_months_date_effective.filtered(lambda x: int(x.payment_reg.month) == month and x.currency_id == x.company_id.currency_id).mapped(
                    'amount')) + sum(payment_all_months_date_effective.filtered(lambda x: int(x.payment_reg.month) == month and x.currency_id != x.company_id.currency_id).mapped('amount_ref')), 4)
            else:
                amount = round(sum(payment_all_months_date_effective.filtered(lambda x: int(x.payment_reg.month) == month and x.currency_id != x.company_id.currency_id).mapped(
                    'amount')) + sum(payment_all_months_date_effective.filtered(lambda x: int(x.payment_reg.month) == month and x.currency_id == x.company_id.currency_id).mapped('amount_ref')), 4)
            return amount

        res = {
            'desde':   str(self.desde.strftime("%d/%m/%Y")),
            'hasta':     str(self.hasta.strftime("%d/%m/%Y")),
            'type_report': self.type_report,
            'company_name': self.company_id.name,
            'currency_id': 'USD' if self.currency_id.name == 'USD' else 'VEF',
            'report_currency': 'USD' if self.report_currency == 'usd' else 'VEF',
            'journal_id': ', '.join([str(i) for i in self.journal_id.mapped('name')]),
            'company_vat':  self.company_id.vat,
            'invoices':     datas,
            'data_difference':     data_difference,
            'total_amount_difference':     total_amount_difference,
            'total_amount_ref_difference':     total_amount_ref_difference,
            'journals':     journals,
            'total_amount':round(total_amount,4),
            'total_amount_ref':round(total_amount_ref,4),
            # ==================================================================================== #
            'enero_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 1),
            'febrero_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 2),
            'marzo_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 3),
            'abril_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 4),
            'mayo_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 5),
            'junio_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 6),
            'julio_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 7),
            'agosto_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 8),
            'septiembre_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 9),
            'octubre_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 10),
            'noviembre_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 11),
            'diciembre_date_effective': get_amount_month(self.report_currency, payment_all_months_date_effective, 12),
            # ==================================================================================== #       
            # Montos por método de pago:
            'efectivo_usd': round(efectivo_usd, 4),
            'efectivo_bs': round(efectivo_bs, 4),
            'banco_usd': round(banco_usd, 4),
            'banco_bs': round(banco_bs, 4),
            # Listado de meses:
            'month_list': month_list
        }
        data = {
            'form': res,
        }
        return self.env.ref('eu_account_reports.custom_action_cobros_por_numero_multimoneda_wizard').report_action([],data=data)