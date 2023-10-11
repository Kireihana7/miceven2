# -*- coding: utf-8 -*-
#flagship----aqui cambiamos el calculo del emonto en ingles
from odoo.exceptions import UserError
from odoo import models, fields,api,_
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from ..models.test import numero_to_letras,convierte_cifra
TODAY=date.today()
class HRContact(models.Model):
    _name = 'hr.contract'
    _inherit = ['hr.contract','mail.thread', 'mail.activity.mixin']

    def numero_to_letras_contract(self,numero):
        return numero_to_letras(numero)
    def _get_calendario_feriado(self):
        for rec in self:
            thisdateyear=rec.date_start.year
            thisyear=TODAY.year
            if self.env['hr.holidays.per.year'].search([('anno_abo','=',thisdateyear)],order='id desc', limit=1):
                return self.env['hr.holidays.per.year'].search([('anno_abo','=',thisdateyear)],order='id desc', limit=1)
            else:
                return self.env['hr.holidays.per.year'].search([('anno_abo','=',thisyear)],order='id desc', limit=1)
    def alert_end_of_contract(self):
        days_of_grace=self.env['ir.config_parameter'].sudo().get_param('l10n_ve_payroll.days_alert_contract')
        contracts=self.env['hr.contract'].sudo().search([('is_indetermined','=',False),('date_end','!=',False),('date_end','>=',TODAY),('date_end','<=',TODAY+relativedelta(days=int(days_of_grace)))])
        users_admins=self.env.ref('hr_payroll.group_hr_payroll_manager').users
        for user in users_admins:
                if contracts.filtered(lambda x:x.company_id in user.company_ids):#contracts and not set(contracts.mapped('company_id')).isdisjoint(set(user.company_ids)):
                    notification_obj = self.env['mail.notification']
                    msjbody="<div><p>Estimado Administrador de Nómina.</p><p>Existen algunos contratos que estan proximos a vencer.</p><p>Quizas le interese revisar los contratos</p>"
                    for contract in contracts.filtered(lambda x:x.company_id in user.company_ids):
                        msjbody+=f"<p><a href='#' data-oe-id='{contract.id}' data-oe-model='hr.contract'>{contract.name}</a></p>"

              
                    contracts.filtered(lambda x:x.company_id in user.company_ids).activity_schedule(
                        "l10n_ve_payroll.expiring_contracts_activity_type",
                        date.today(),
                        summary="contratos por revisar",
                        note='Este Contrato esta proximo a vencer',
                        user_id=user.id,
                    )
                    
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        pass
    @api.onchange('employee_id')
    def _onchange_empoyee(self):
            for rec in self:
                if rec.employee_id:
                    rec.analytic_account_id=rec.employee_id.cost_center
    currency_id_dif = fields.Many2one("res.currency", 
        string="Referencia en Divisa",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),)
    is_liquidado=fields.Boolean("Este contrato esta liquidado")
    # sal_comple = fields.Float(string="Salario Complementario")
    @api.depends('wage','currency_id_dif','currency_id','tax_today','complemento','cesta_ticket')
    def _amount_all_usd(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            record[("amount_total_usd")]    = (+record.wage+record.cesta_ticket) * record.tax_today + record.complemento
#.currency_id._convert(record['wage'], record.currency_id_dif, record.company_id or record.env.company, fields.date.today())

    # @api.depends('amount_total_usd','tax_today')
    # def _amount_all_usd_bs(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     for record in self:
    #         record[("wage")] = record.amount_total_usd * record.tax_today
    
    @api.depends('currency_id_dif')
    def _name_ref(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            record[("name_rate")] = record.currency_id_dif.currency_unit_label
    
    @api.depends('currency_id_dif','currency_id')
    def _tax_today(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
                record[("tax_today")] = record.currency_id_dif.rate


    tax_today= fields.Float(readonly=True, compute="_tax_today",digits=(20,4)) 
    name_rate= fields.Char(store=True,readonly=True, compute='_name_ref')        
    amount_total_usd = fields.Float(string='Salario (USD)', readonly=False, tracking=4, default=0,compute='_amount_all_usd')
    
    wage=fields.Float(compute='_amount_all_usd_bs',store=True,readonly=False,tracking=True)
    ret_inces=fields.Float(string="Retención INCES %",tracking=True)
    complemento = fields.Float(store=True, readonly=False, string='Bono P. Social',tracking=True)
    struct_id=fields.Many2one('hr.payroll.structure',string="Estructura",tracking=True)
    basado_usd = fields.Boolean('Basado en USD')
    cesta_ticket=fields.Float(string="Cesta Alimenticia",tracking=True)
    historial_wage=fields.One2many('salary.historial.lines','parent_id',tracking=True)
    ret_judicial_check=fields.Boolean(string="Retencion judicial",tracking=True)
    ret_judicial=fields.Float()
    @api.constrains("employee_id")
    def _constraint_already_contracted(self):
        if self.search([('employee_id','=',self.employee_id.id),('company_id','=',self.env.company.id),('id','!=',self.id),('state','not in',['close','cancel'])]):
            raise UserError ("Ya existe un contrato vinculado a este empleado")
    
    def write(self,vals):
        # no esta haciendo los vals si no los tiene
        res=super().write(vals)
        for rec in self:
            
            if rec.id==rec.employee_id.contract_id.id and rec.employee_id.job_title != rec.job_id.name:
                if len(rec.employee_id.historico_trabajos)==0 or rec.job_id.name != rec.employee_id.historico_trabajos[-1].job_title:
                    rec.employee_id.historico_trabajos+=self.env['job.history.line'].create({
                        'parent_id':rec.employee_id.id,
                        'job_title':rec.job_id.name,
                        'date_change':TODAY
                    })
                    rec.employee_id.job_title=rec.job_id.name
                    rec.employee_id.job_id=rec.job_id
        
    
        return res
    @api.onchange('wage')
    def _onchange_wage_to_history(self):
        for rec in self:
            if rec.wage:
                historial=list(rec.historial_wage)

                if len(historial)<1 or rec.wage!= historial[-1].salario:
                    rec.historial_wage+=rec.env['salary.historial.lines'].create({
                        'tipo_salario':"Salario Base",
                        'salario':rec.wage
                    })
    @api.onchange('complemento')
    def _onchange_complemento_to_history(self):
        for rec in self:
            if rec.complemento:
                historial=list(rec.historial_wage)

                if len(historial)<1 or rec.complemento!= historial[-1].salario:
                    rec.historial_wage+=rec.env['salary.historial.lines'].create({
                        'tipo_salario':"Complemento",
                        'salario':rec.complemento
                    })
    @api.onchange('cesta_ticket')
    def _onchange_cesta_ticket_to_history(self):
        for rec in self:
            if rec.cesta_ticket:
                historial=list(rec.historial_wage)

                if len(historial)<1 or rec.cesta_ticket!= historial[-1].salario:
                    rec.historial_wage+=rec.env['salary.historial.lines'].create({
                        'tipo_salario':"Cesta Ticket",
                        'salario':rec.cesta_ticket
                    })
    # Sobreescribe el metodo original causando que no se generen entradas mediante el contrato
    def generate_and_change_entries(self,datetime_init,datetime_end):
        for rec in self:
            entries=rec._generate_work_entries2(datetime_init,datetime_end)


            for entry in entries:
                entry._compute_dias_feriados_laborados()
        
    
    def _generate_work_entries(self, date_start, date_stop):
        res=super()._generate_work_entries(date_start,date_stop)
        for x in res:
            if x.date_start.date() in self._get_calendario_feriado().holidays_lines_ids.mapped("fecha"):
                x.sudo().unlink()
        return res
    def _generate_work_entries2(self,date_start, date_stop):
            vals_list = []

            # In case the date_generated_from == date_generated_to, move it to the date_start to
            # avoid trying to generate several months/years of history for old contracts for which
            # we've never generated the work entries.
           
            # For each contract, we found each interval we must generate
            contract_start = fields.Datetime.to_datetime(date_start)
            contract_stop = datetime.combine(fields.Datetime.to_datetime(date_stop or datetime.max.date()), datetime.max.time())
            last_generated_from = min(self.date_generated_from, contract_stop)
            date_start_work_entries = max(date_start, contract_start)
            date_stop_work_entries = min(date_stop, contract_stop)
            self.date_generated_from = date_start_work_entries
            self.date_generated_to = date_stop_work_entries

            # last_generated_to = max(self.date_generated_to, contract_start)

            vals_list.extend(self._get_work_entries_values(contract_start, date_stop_work_entries))
            calendario=self._get_calendario_feriado().holidays_lines_ids.mapped("fecha") if self._get_calendario_feriado() else False
            if not vals_list:
                return self.env['hr.work.entry']
            for x in vals_list:
                if x['date_start'].date() in calendario:
                    vals_list.remove(x)
            return self.env['hr.work.entry'].create(vals_list)

    def button_status_cancel(self):
        for rec in self:
            rec.state="cancel"
    def button_status_advance(self):
        for rec in self:
            if rec.state=='draft':
                rec.state="open"
            elif rec.state=="open":
                rec.state="close"


# apartir de aca es toda la bola del contrato fijo
    number_of_renovations=fields.Integer(tracking=True)
    is_labor_determined=fields.Boolean(string="¿Es obra determinada?",tracking=True)
    is_indetermined=fields.Boolean(string="¿Es empleado fijo?",tracking=True)
    is_variable_wage=fields.Boolean(string="¿Posee un salario variable?",tracking=True)

    @api.onchange('is_labor_determined')
    def onchange_labor_determined(self):
        for rec in self:
            if rec.is_labor_determined:
                rec.is_indetermined=False
    @api.onchange('is_indetermined')
    def onchange_fijo(self):
        for rec in self:
            if rec.is_indetermined:
                rec.date_end=False
                rec.state="open"
                rec.is_labor_determined=False
    def renovacion_contrato(self):
        for rec in self:
            if rec.is_indetermined:
                raise UserError("No puede renovarse un contrato fijo")
            return {
                    'type':'ir.actions.act_window',
                    'res_model':'hr.renew.contract',
                    'view_mode':'form',
                    'target':'new',
                    'binding_model_id':False,
                } 

    class SalaryHistorialLines(models.Model):
        _name="salary.historial.lines"
        _description="lleva los cambios en el salario"

        parent_id=fields.Many2one('hr.contract')
        tipo_salario=fields.Char('Tipo de Salario')
        salario=fields.Float(string="Monto")
        fecha=fields.Date(string="Fecha",default=fields.Date.today(),readonly=True)


         
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
