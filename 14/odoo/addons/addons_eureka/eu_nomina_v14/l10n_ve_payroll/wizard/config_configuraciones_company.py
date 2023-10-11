from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrConfigCompanyWiz(models.TransientModel):
    _name = 'hr.config.company.wiz'
    _description="Configura las cuentas contables a donde iran los asientos de las prestaciones"

    dias_vac_base=fields.Integer("Dias de vacaciones",default=lambda self: self.env.company.dias_vac_base)
    cant_dias_utilidades=fields.Integer("Dias utilidades",default=lambda self: self.env.company.cant_dias_utilidades)
    horas_change_noche=fields.Float(string="valor en horas extra para cambio a nocturno",default=lambda self: self.env.company.horas_change_noche)
    num_cuenta_faov=fields.Char("N° Inscrip. FAOV",size=20,default=lambda self: self.env.company.num_cuenta_faov)
    banavih_account=fields.Char("N° AF. BANAVIH",default=lambda self: self.env.company.banavih_account)
    cesta_ticket = fields.Float(string = 'Cesta ticket Socialita', default=lambda self: self.env.company.cesta_ticket)
    sal_minimo_ley= fields.Float(string="Salario Minimo de Ley",default=lambda self: self.env.company.sal_minimo_ley)
    por_riesgo = fields.Float(string='% Riesgo Empresa SSO', default=lambda self: self.env.company.por_riesgo)
    por_aporte_sso = fields.Float(string='% Aporte Empleado SSO', default=lambda self: self.env.company.por_aporte_sso)
    por_empresa_lph = fields.Float(string='% Aporte Empresa LPH', default=lambda self: self.env.company.por_empresa_lph)
    por_empleado_lph = fields.Float(string='% Aporte Empleado LPH', default=lambda self: self.env.company.por_empleado_lph)
    por_empresa_rpe = fields.Float(string='% Aporte Empresa RPE', default=lambda self: self.env.company.por_empresa_rpe)
    por_empleado_rpe = fields.Float(string='% Aporte Empleado RPE', default=lambda self: self.env.company.por_empleado_rpe)
    check_journey_rotations=fields.Boolean("habilitar rotación",default=lambda self: self.env.company.check_journey_rotations)
    time_between_rotations=fields.Integer("Tiempo en dias para la rotacion de grupos",default=lambda self: self.env.company.time_between_rotations)
    days_alert_contract=fields.Integer('Diás de alerta vencimiento contrato',default=lambda self: self.env['ir.config_parameter'].sudo().get_param('l10n_ve_payroll.days_alert_contract'))
    create_work_entry_with_attendance=fields.Boolean('Crear entrada laboral con asistencia',default=lambda self: self.env['ir.config_parameter'].sudo().get_param('l10n_ve_payroll.create_work_entry_with_attendance'))
    boss_rrhh=fields.Many2one('hr.employee',string='Jefe Recursos humanos', default=lambda self: self.env.company.boss_rrhh)
    lawyer_ref=fields.Many2one('hr.employee',string='Abogado redactor', default=lambda self: self.env.company.lawyer_ref)
    num_ipsa=fields.Char(string='IPSA. Nº ', default=lambda self: self.env.company.num_ipsa)
    registrofiscal=fields.Char(string='Registro Fiscal de la empresa', default=lambda self: self.env.company.registrofiscal)
    subproceso=fields.Char("Subproceso compañia")
    
    
    def configurar(self):

        compania=self.env.company
        
        if self.registrofiscal:
            compania.registrofiscal=self.registrofiscal
        if self.subproceso:
            compania.subproceso=self.subproceso

        if self.lawyer_ref:
            compania.lawyer_ref=self.lawyer_ref

        if self.num_ipsa:
            compania.num_ipsa=self.num_ipsa

        if self.boss_rrhh:
            compania.boss_rrhh=self.boss_rrhh

        if self.dias_vac_base:

            compania.dias_vac_base=self.dias_vac_base
        if self.cant_dias_utilidades:

            compania.cant_dias_utilidades=self.cant_dias_utilidades
        if self.horas_change_noche:

            compania.horas_change_noche=self.horas_change_noche
        if self.num_cuenta_faov:

            compania.num_cuenta_faov=self.num_cuenta_faov
        if self.banavih_account:

            compania.banavih_account=self.banavih_account
        if self.cesta_ticket:

            compania.cesta_ticket=self.cesta_ticket
        if self.sal_minimo_ley:

            compania.sal_minimo_ley=self.sal_minimo_ley
        if self.por_riesgo:

            compania.por_riesgo=self.por_riesgo
        if self.por_aporte_sso:

            compania.por_aporte_sso=self.por_aporte_sso
        if self.por_empresa_lph:

            compania.por_empresa_lph=self.por_empresa_lph
        if self.por_empleado_lph:

            compania.por_empleado_lph=self.por_empleado_lph
        if self.por_empresa_rpe:

            compania.por_empresa_rpe=self.por_empresa_rpe
        if self.por_empleado_rpe:

            compania.por_empleado_rpe=self.por_empleado_rpe
        if self.check_journey_rotations:

            compania.check_journey_rotations=self.check_journey_rotations
        if self.time_between_rotations:
            compania.time_between_rotations=self.time_between_rotations
        
        if self.days_alert_contract:
            self.env['ir.config_parameter'].set_param('l10n_ve_payroll.days_alert_contract',self.days_alert_contract)
        if self.create_work_entry_with_attendance:
            self.env['ir.config_parameter'].set_param('l10n_ve_payroll.create_work_entry_with_attendance',self.create_work_entry_with_attendance)

