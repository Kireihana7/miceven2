# -*- coding:utf-8 -*-


from odoo import models, fields, api, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips


class HrPayslipStruct(models.Model):
    _inherit = "hr.payslip.run"
    _description = "Nomina Especial"

    check_special_struct = fields.Boolean('Nomina Especial')
    struct_id = fields.Many2one('hr.payroll.structure', 'Tipo de Nomina Especial',
                                states={'draft': [('readonly', False)]})

    @api.onchange('check_special_struct')
    def onchange_check_special_struct(self):
        res = {}
        if not self.check_special_struct:
            res = {'value': {'struct_id_payroll': False}}
        return res


class HrPayrollStructureSpecial(models.Model):
    _inherit = 'hr.payroll.structure'
    _description = "Employee familiar"

    STRUCT_CATEGORY = [
        ('normal', 'Normal'),
        ('especial', 'Especial'),
    ]

    PAYROLL_CATEGORY = [
        ('ticket', 'Cestatickets'),
        ('fideicomiso', 'Fideicomiso'),
        ('vacaciones', 'Vacaciones'),
        ('utilidad', 'Utilidades'),
        ('liquidacion', 'Liquidaciones'),
        ('militar', 'Militar'),
        ('habitacional', 'Banavih'),
        ('gurderia', 'Guarderia'),
    ]

    # DEDUCTION_MODE = [
    #     ('star_m', 'Primera quincena'),
    #     ('end_m', 'Fin de mes'),
    #     ('iq', 'Cada pago')
    # ]

    struct_category = fields.Selection(STRUCT_CATEGORY, 'Categoria de Nomina', index=True, required=True)
    struct_id_payroll_category = fields.Selection(PAYROLL_CATEGORY, 'Referencia de Nómina categoría')
    struct_id_reference = fields.Many2one('hr.payroll.reference', 'Referencia de Nómina')
    code = fields.Char(required=True, help="Este código puede ser usado en las reglas salariales.")
    # deductions_pay_mode = fields.Selection(DEDUCTION_MODE, 'Deducciones a:',default='iq')


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def get_all_structures(self):
        # ret = super(hr_contract, self).get_all_structures(cr, uid, contract_ids, context=context)
        # is_special = self._context.get('is_special', False)
        active_id = self._context.get('active_id', False)
        special_fields = self.env['hr.payslip.run'].search([('id', '=', active_id)])
        is_special = special_fields.check_special_struct
        if is_special:
            # hrpr = self.env['hr.payslip.run'].search([('id', '=', active_id)])
            structure_ids = [special_fields.struct_id.id]
        else:
            # Si es una nomina especial asigna el mismo id de nomina a cada contrato
            # if hrpr.check_special_struct and hrpr.struct_id:
            # structure_ids = [hrpr.struct_id.id]
            # else:
            structure_ids = [contract.struct_id.id for contract in self if contract.struct_id]

        if not structure_ids:
            return []
        local_parent = self.env['hr.payroll.structure']._get_parent_structure()
        if local_parent:
            return list(set(local_parent.id))
        return structure_ids



class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                # check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                # set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()

    def compute_sheet(self):
        # ctx = self.context.copy()
        payslip_run_obj = self.env['hr.payslip.run']
        come_from = self._context.get('come_from', False)
        if come_from and come_from == 'payoff':
            for ps in self:
                self.with_context({'is_special': 1, 'special_id': ps.struct_id.id, 'slip_id': self.ids[0]})
        else:
            for ps in self:
                for psr in payslip_run_obj.browse(ps.payslip_run_id.id):
                    is_special = psr.check_special_struct
                    if is_special:
                        self.struct_id = psr.struct_id.id
                        self.with_context({'is_special': 1, 'special_id': psr.struct_id.id})
        ret = super(HrPayslip, self).compute_sheet()
        return ret


class HrPayrollReference(models.Model):
    _name = 'hr.payroll.reference'
    _description = "Referencia para Nominas Especiales"

    name = fields.Char('Referencia de Nómina', size=20)
    description = fields.Char('Descripcion de la Referencia de Nómina')
