# -*- encoding: utf-8 -*-


#PragmaTIC (om) 2015-07-03 actualiza para version 8
from unicodedata import category
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
class ResCompany(models.Model):

    _inherit = 'res.company'
    is_no_lucrative=fields.Boolean('¿Es una empresa sin fines de lucro?',tracking=True)
    cesta_ticket = fields.Float(string = 'Cesta ticket Socialita', default=200000,tracking=True)
    sal_minimo_ley= fields.Float(string="Salario Minimo de Ley",tracking=True)
    por_riesgo = fields.Float(string='% Riesgo Empresa SSO', default=10,tracking=True)
    por_aporte_sso = fields.Float(string='% Aporte Empleado SSO', default=4,tracking=True)

    por_empresa_lph = fields.Float(string='% Aporte Empresa LPH', default=2,tracking=True)
    por_empleado_lph = fields.Float(string='% Aporte Empleado LPH', default=1,tracking=True)

    por_empresa_rpe = fields.Float(string='% Aporte Empresa RPE', default=2,tracking=True)
    por_empleado_rpe = fields.Float(string='% Aporte Empleado RPE', default=0.5,tracking=True)
    num_cuenta_faov=fields.Char("N° Inscrip. FAOV",size=20,tracking=True)
    dias_vac_base=fields.Integer("Dias de vacaciones",default=15,tracking=True)
    cant_dias_utilidades=fields.Integer("Dias utilidades",default=15,tracking=True)
    horas_change_noche=fields.Float(string="valor en horas extra para cambio a nocturno",default=4,tracking=True)
    ut=fields.Many2one('tributary.unit',string="Unidad Tributaria", compute="_get_ut",tracking=True)
    banavih_account=fields.Char("N° AF. BANAVIH",tracking=True)
    time_between_rotations=fields.Integer("Tiempo en dias para la rotacion de grupos",tracking=True)
    check_journey_rotations=fields.Boolean("habilitar rotación",tracking=True)
    boss_rrhh=fields.Many2one('hr.employee',string='Jefe Recursos humanos',tracking=True)
    lawyer_ref=fields.Many2one('hr.employee',string='Abogado redactor',tracking=True)
    num_ipsa=fields.Char(string='IPSA. Nº ',tracking=True)
    registrofiscal=fields.Char(string='Registro Fiscal de la empresa',tracking=True)
    subproceso=fields.Char("Subproceso compañia",tracking=True)
    sent_txt_to_folder=fields.Boolean("Enviar txts a la carpeta",tracking=True)
# asientos de las prestaciones
# diario base para eso
    journal_for_prestaciones=fields.Many2one("account.journal",tracking=True)

#Prestacion
    asiento_prestaciones=fields.Many2one("account.account",tracking=True)
    asiento_interes_pres=fields.Many2one("account.account",tracking=True)
    asiento_antiguedad_p=fields.Many2one("account.account",tracking=True)
    asiento_interes_paga=fields.Many2one("account.account",tracking=True)
#Anticipo
    asiento_anticipo=fields.Many2one("account.account",tracking=True)
    asiento_interes_anti=fields.Many2one("account.account",tracking=True)
    asiento_antiguedad_anti_p=fields.Many2one("account.account",tracking=True)
    asiento_interes_anti_paga=fields.Many2one("account.account",tracking=True)


#Liquidación
    asiento_liq_int_pagar=fields.Many2one("account.account",tracking=True)
    asiento_liq_pag_pendi=fields.Many2one("account.account",tracking=True)

#estructuras para la liquidacion

    struct_vacaciones=fields.Many2one("hr.payroll.structure",tracking=True)
    struct_liquidacion=fields.Many2one("hr.payroll.structure",tracking=True)

#Balance de la compañia

    Balance=fields.Float()

    def cromium_rotate_worker_groups(self):

            companies=self.env['res.company'].sudo().search([('check_journey_rotations','=',True)])


            for c in companies:

                groups=self.env['hr.employee.journey.group'].sudo().search([('company_id','=',c.id)])
                category_groups=list(set(groups.mapped('categoria')))
                for categoria in category_groups:
                    groups_auxiliar=groups.filtered(lambda x: x.categoria==categoria).sorted(key=lambda x: x.sequence)
                    employee_ids_new=groups_auxiliar[-1].employee_ids
                    
                    for g in groups_auxiliar:
                        employee_ids_aux=g.employee_ids
                        g.employee_ids=employee_ids_new
                        employee_ids_new=employee_ids_aux
                        g.change_contract_schedule()
                





    def _get_ut(self):
        for rec in self:
            rec.ut=self.env['tributary.unit'].search([],limit=1,order="id asc")

    # @api.constrains('cant_dias_utilidades',)
    # def constrain_dias_util(self):
    #     for rec in self:
    #         if rec.cant_dias_utilidades<30 or rec.cant_dias_utilidades>120:
    #             raise UserError('los dias de utilidades no pueden ser menores de 30 ni mayores de 120')