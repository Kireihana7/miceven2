# -*- coding: utf-8 -*-

#import numpy as np
#import numpy_financial as npf
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Modelo para manejar los prestamos de los empleados"
    _rec_name = "name"

    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company.id,tracking=True,invisible=True)
    name = fields.Char("Nombre", help=u"Nombre del préstamo")
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Empleado",tracking=True)
    financial_partner_id = fields.Many2one('res.partner', string="Financiera",tracking=True)
    start_date = fields.Date("Fecha de inicio",tracking=True)
    amount = fields.Float(u"Monto del préstamo",tracking=True)
    state = fields.Selection([('draft', 'Borrador'), ('approved', 'Aprobado'), ('paid', 'Pagado'), ('cancel', 'Cancelado')],
                             string="Estado", default='draft',tracking=True)
    loan_line_ids = fields.One2many(comodel_name='hr.employee.loan.line', inverse_name='loan_id', string="Líneas de préstamo", copy=False,tracking=True)
    next_fee = fields.Integer("Próxima cuota", default=1,tracking=True)
    fee_count = fields.Integer("Cantidad de cuotas", default=0,tracking=True)
    fee_amount = fields.Float("Monto de Cuota",tracking=True)
    rate_id = fields.Many2one('hr.employee.loan.rate', string="Tarifa",tracking=True)
    debt_act_state=fields.Float(string="Saldo deudor", compute="_compute_debt_act_state")

    @api.depends('loan_line_ids','loan_line_ids.paid','loan_line_ids.total','loan_line_ids.date','amount')
    def _compute_debt_act_state(self):
        for rec in self:
            cuotas_unsorted=rec.loan_line_ids.filtered(lambda x: x.paid)
            cuota_sorted_picked=sorted(cuotas_unsorted,key=lambda x: x.date,reverse=True)
            # raise ValidationError([cuota_sorted_picked,type(cuota_sorted_picked)])
            if cuota_sorted_picked:
                rec.debt_act_state=cuota_sorted_picked[0].total
            else:
                rec.debt_act_state=rec.amount


    def get_next_fee(self):
        return self.loan_line_ids.filtered(lambda loan_line: loan_line.number == self.next_fee)

    def approve_loan(self):
        if not self.loan_line_ids:
            raise ValidationError("Primero debe generar las cuotas!")
        self.state = 'approved'

    def cancel_loan(self):
        self.state = 'cancel'

    def set_loan_to_draft(self):
        self.state = 'draft'

    def compute_payment(self):
        if self.fee_count == 0 or self.fee_count is None:
            raise ValidationError("Debe seleccionar la cantidad de cuotas")
        else:
            self.fee_amount = round(self.amount/self.fee_count,2)
            # self.fee_amount = 0

    def compute_fees(self):
        self.ensure_one()
        self.compute_payment()
        self.compute_draft_lines()

    def new_line_vals(self, sequence, date, interest, payment):
        return {
            'loan_id': self.id,
            'number': sequence,
            'date': date,
            'interest': interest,
            'payment': payment,
            'dues': payment + interest,
            'rate': self.rate_id.rate,
        }

    def compute_draft_lines(self):
        self.ensure_one()
        self.loan_line_ids.unlink()
        amount = self.amount

        if self.start_date:
            date = self.start_date
        else:
            date = datetime.today().date()
        if self.rate_id.type == 'daily':
            delta = relativedelta(days=1)
        elif self.rate_id.type == 'weekly':
            delta = relativedelta(weeks=1)
        elif self.rate_id.type == 'bi-weekly':
            delta = relativedelta(weeks=2)
        elif self.rate_id.type == 'monthly':
            delta = relativedelta(months=1)
        elif self.rate_id.type == 'bimonthly':
            delta = relativedelta(months=2)

        for i in range(1, self.fee_count + 1):
            interest = amount * self.rate_id.rate / 100
            payment = self.fee_amount - interest

            line = self.env['hr.employee.loan.line'].create(
                self.new_line_vals(i, date, interest, payment)
            )
            # line.check_amount()
            date += delta
            amount -= line.dues - line.interest
            line.total = amount


class HrEmployeeLoanLine(models.Model):
    _name = 'hr.employee.loan.line'
    _description = 'Cuotas'

    loan_id = fields.Many2one("hr.employee.loan", string="Préstamo")
    number = fields.Integer(string=u"Número")
    date = fields.Date(string="Fecha")
    rate = fields.Float(string="Tarifa", digits=(8, 4))
    dues = fields.Float(string="Cuota")
    payment = fields.Float(string="Abono")
    total = fields.Float(string="Saldo Final")
    interest = fields.Float(string="Interes")
    paid = fields.Boolean(string="Pagada", compute='_compute_paid')
    payslip_id = fields.Many2one(comodel_name="hr.payslip", string=u"Nómina")
    date_paid = fields.Date(string="Fecha de pago", related="payslip_id.date_to")

    @api.depends('payslip_id', 'payslip_id.state')
    def _compute_paid(self):
        for rec in self:
            rec.paid = True if rec.payslip_id and rec.payslip_id.state == 'done' else False



class HrEmployeeLoanRate(models.Model):
    _name = 'hr.employee.loan.rate'
    _description = 'Tarifas'
    _rec_name = 'name'

    types = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('bi-weekly', 'Quincenal'),
        ('monthly', 'Mensual'),
        ('bimonthly', 'Bimensual'),
    ]

    name = fields.Char(string="Nombre", required=True)
    type = fields.Selection(types, string="Tipo", required=True)
    rate = fields.Float(string="Tarifa", digits=(8, 5), required=True)






