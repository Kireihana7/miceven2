# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    total_to_pay = fields.Float(compute='_compute_worked_hours', store=True)
    real_worked_hours = fields.Float()

    @api.depends('line_ids')
    def _compute_worked_hours(self):
        for register in self.filtered('line_ids'):
            total_amount = register.line_ids.filtered(lambda line: line.code == 'NET').total or 0.0
            register.total_to_pay = total_amount

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        self.input_line_ids = [(0, 0, {'input_type_id': input.id}) for input in self.struct_id.input_line_type_ids if input.id not in self.input_line_ids.mapped('input_type_id').ids]
        res = super(HrPayslip, self)._onchange_employee()
        discount_import_ids = self.env['payroll.discount.import'].search([('employee_id', '=', self.employee_id.id),
                                                                          ('date_from', '>=', self.date_from),
                                                                          ('date_to', '<=', self.date_to)])
        codes = []
        for line in discount_import_ids:
            if line.discount_code not in codes:
                codes.append(line.discount_code)
        discount_amount_dict = {}
        for code in codes:
            amount = 0
            for discount in discount_import_ids.filtered(lambda di: di.discount_code == code):
                amount += discount.amount
            discount_amount_dict.update({code: amount})

        for code, amount in discount_amount_dict.items():
            element = self.input_line_ids.filtered(lambda di: di.code == code)
            if element:
                element[0].amount = amount

        working_hours_import_ids = self.env['working.hours.import'].search([('employee_id', '=', self.employee_id.id),
                                                                                ('date_from', '>=', self.date_from),
                                                                                ('date_to', '<=', self.date_to)])
        normal_hours = sum(working_hours_import_ids.mapped('hours_amount'))
        extra_hours = sum(working_hours_import_ids.mapped('extra_hours_amount'))
        holiday_hours = sum(working_hours_import_ids.mapped('holiday_hours_amount'))

        element = self.worked_days_line_ids.filtered(lambda di: di.code == 'WORK100')
        if element:
            element[0].number_of_hours = normal_hours

        for input in self.input_line_ids.filtered(lambda ipi: ipi.code in ['HE35', 'HE100', 'FINAN']):
            if input.code == 'HE35':
                input.amount = extra_hours
            if input.code == 'HE100':
                input.amount = holiday_hours
            # get every approved loan next fee
            if input.code == 'FINAN':
                finan_amount = 0.0
                loan_fees = []
                if self.employee_id.get_approved_loans():
                    for loan in self.employee_id.get_approved_loans():
                         # si la fecha es en el rango
                        loan_fees.append(loan.get_next_fee().dues)
                    finan_amount = sum(loan_fees)
                if self.pay_vacation and self.vacation_type == 'enjoyed':
                    input.amount = (finan_amount + self.contract_id.fixed_loan) * 2
                else:
                    input.amount = finan_amount + self.contract_id.fixed_loan
            if input.code == 'AHORRO':
                if self.pay_vacation and self.vacation_type == 'enjoyed':
                    input.amount = self.contract_id.amount_saved * 2
                else:
                    input.amount = self.contract_id.amount_saved

        return res

    

    pay_vacation = fields.Boolean(string="Vacaciones",
                                  help="Seleccione si el empleado va a cobrar vacaciones")
    vacation_type = fields.Selection([('enjoyed', 'Vacaciones disfrutadas'),
                                      ('worked', 'Vacaciones trabajadas'),
                                      ('unpayed', 'Vacaciones disfrutadas sin adelanto')],
                                       string="Tipo de vacaciones")

    partial_worked_days = fields.Boolean(string=u"Días trabajados parciales", help='Usar por ejemplo si un empleado entró a mitad de quincena (No usar si el empleado cobra por hora)')

    def compute_commission_amount(self, payslip):
        payment_domain = [('payment_date', '<=', payslip.date_to),
                          ('state', 'in', ['posted', 'sent', 'reconciled']),
                          ('commissioned', '=', False),
                          ('user_id', '=', payslip.employee_id.user_id.id)]
        payment_fields = ['id', 'amount', 'amount_tax']
        payments_by_employee = payslip.env['account.payment'].search_read(payment_domain, payment_fields)

        payments_amount = sum([p.get('amount') - p.get('amount_tax') for p in payments_by_employee])
        commission_amount = (payments_amount * payslip.contract_id.comission_rate) / 100
        for line in payslip.input_line_ids:
            if line.code == 'COMIVE':
                line.amount = commission_amount

    def compute_sheet(self):
        # computar segunda quincena con if pay_vacation and vacation_type
        # obtener nomina anterior y revisar lo anterior,
        # si es verdadero establecer todos los line_ids en 0

        contract_wages = {}  # este diccionario es para almacenar salarios y actualizarlos después en los contratos correspondientes
        # para suplir la necesidad de un empleado que trabajo quincena parcial o que gana por hora

        for rec in self:

            if rec.partial_worked_days:
                contract_wages.update({rec.contract_id.id: rec.contract_id.wage})
                rec.contract_id.wage = (rec.contract_id.wage / 23.83) * sum([line.number_of_days for line in rec.worked_days_line_ids])
            if rec.contract_id.schedule_pay == 'hourly':
                contract_wages.update({rec.contract_id.id: rec.contract_id.wage})
                rec.contract_id.wage = rec.contract_id.wage * sum([line.number_of_hours for line in rec.worked_days_line_ids])
            

            #Compute comission amount based on contract commision rate and payed invoices by employee
           

        super(HrPayslip, self).compute_sheet()

        if contract_wages:
            for rec in self.env['hr.contract'].browse([id for id in contract_wages.keys()]):
                index = '{}'.format(rec.id)
                rec.message_post()
                rec.wage = contract_wages[int(index)]
        ##############################################################
        # duplicate company contributions if vacation type is enjoyed
        


        ##############################################################

        
        return True

    def action_mail_send(self):
        template_id = self.env.ref('eu_dom_payroll.email_template_mass_send')
        template_id.send_mail(self.id, force_send=True)
