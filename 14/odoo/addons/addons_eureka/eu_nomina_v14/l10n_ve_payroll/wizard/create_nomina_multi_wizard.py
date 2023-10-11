# -*- coding: utf-8 -*-




from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrPayslipEmployees_2(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def get_date_ini(self):
            try:
                if self._context.get('active_model')=='hr.payslip.run':
                    return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))]).date_start
                else:
                    return False
            except:
                return False
    def get_date_fin(self):
            try:
                if self._context.get('active_model')=='hr.payslip.run':
                    return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))]).date_end
                else:
                    return False
            except:
                return False
    def get_date_category_id(self):
            try:
                if self._context.get('active_model')=='hr.payslip.run':
                    return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))]).category_id_filter
                else:
                    return False
            except:
                return False
    
    fecha_ini=fields.Date(string="fecha ini",default=get_date_ini)
    fecha_fin=fields.Date(string="fecha fin",default=get_date_fin)
    category_id=fields.Many2one('hr.employee.category',string="category",default=get_date_category_id)
    def _get_available_contracts_domain(self):
        
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        
        run=self.env[active_model].search([('id','=',active_ids)],limit=1)
        domain=[('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]
        if run.department_id_filter:
            domain.append(('department_id','=',run.department_id_filter.id))
        if run.category_id_filter:
            domain.append(('category_ids','=',run.category_id_filter.id))
        if run.job_id_filter:
            domain.append(('contract_id.job_id','=',run.job_id_filter.id))
        if run.struct_id and (run.check_special_struct==False and run.vacation==False):
            domain.append(('contract_id.struct_id','=',run.struct_id.id))
        if run.ignorate_on_vacations:
            domain.append(('in_vacations_till','=',False))
        if run.search_with_vacations:
            domain.append(('has_vacations_loose','=',True))
        return domain

    def _get_employees(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        
        run=self.env[active_model].search([('id','=',active_ids)],limit=1)
        # YTI check dates too
        if run.search_with_vacations:
            return self.env['hr.employee'].search(self._get_available_contracts_domain()).filtered(lambda x:x.has_vacations_loose)
        else:
            return self.env['hr.employee'].search(self._get_available_contracts_domain())
    
    @api.model
    def default_get(self, fields):
        result = super(HrPayslipEmployees_2, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_ids or active_model != 'hr.payslip.run':
            return result
        struct = self.env[active_model].browse(self._context.get('active_ids')).struct_id
        result.update({
            'structure_id':struct.id,
                        })
        return result
    
    # reescritura del anterior para asegurar que reciba las vacaciones
    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)


        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        run=self.env[active_model].search([('id','=',active_ids)],limit=1)
        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            values = dict(default_values, **{
                'name':'draft payslip',
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
                'tax_today':payslip_run.tax_today
            })
            if run.vacation: 
                values['is_vacation']=True
            if run.is_utility==True:
                values['is_utility']=True
            payslip = self.env['hr.payslip'].create(values)
            payslip._onchange_employee()
            payslips += payslip
            if run.incidence_line_ids:
                for line in run.incidence_line_ids.filtered(lambda x: contract.employee_id in x.employee_ids):
                    incidenceline=payslip.worked_days_line_ids.filtered(lambda x:x.work_entry_type_id.id==line.work_entry_type.id)[:1]
                    if incidenceline.filtered(lambda x:x.is_incidence):
                        if line.hours_or_days=='hour':
                           incidenceline.number_of_hours=line.number_of_unit
                        else:
                            incidenceline.number_of_days=line.number_of_unit
                        
                    elif incidenceline:
                        if line.hours_or_days=='hour':
                           incidenceline.number_of_hours=incidenceline.number_of_hours + line.number_of_unit
                        else:
                            incidenceline.number_of_days=incidenceline.number_of_days + line.number_of_unit
                        
                    else:
                        data={
                            'payslip_id':payslip.id,
                            'work_entry_type_id':line.work_entry_type.id,
                            'name':'INCIDENCIA-'+line.work_entry_type.name,
                            'display_name':'INCIDENCIA-'+line.work_entry_type.name,
                            'is_incidence':True
                        }
                        if line.hours_or_days=='hour':
                            data['number_of_hours']=line.number_of_unit
                        else:
                            data['number_of_days']=line.number_of_unit
                        payslip.worked_days_line_ids+=self.env['hr.payslip.worked_days'].create(data)
                payslip.has_incidencias=True
        # payslip_run.compute_all_payslips()
        payslip_run.state = 'verify'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }