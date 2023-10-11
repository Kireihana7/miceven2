from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrConfigPrestacion(models.TransientModel):
    _name = 'hr.config.prestaciones.wiz'
    _description="Configura las cuentas contables a donde iran los asientos de las prestaciones"

    journal_for_prestaciones=fields.Many2one("account.journal",default= lambda self: self.env.company.journal_for_prestaciones)
# Prestacion
    asiento_prestaciones=fields.Many2one("account.account",string="Cuenta deudora prest.",default= lambda self: self.env.company.asiento_prestaciones)
    asiento_interes_pres=fields.Many2one("account.account",string="Cuenta deudora int. prest.",default= lambda self: self.env.company.asiento_interes_pres)
    asiento_antiguedad_p=fields.Many2one("account.account",string="Cuenta acreedora prest.",default= lambda self: self.env.company.asiento_antiguedad_p)
    asiento_interes_paga=fields.Many2one("account.account",string="Cuenta acreedora int. prest.",default= lambda self: self.env.company.asiento_interes_paga)
#Anticipo
    asiento_anticipo=fields.Many2one("account.account",string="Cuenta deudora anticip.",default= lambda self: self.env.company.asiento_anticipo)
    asiento_interes_anti=fields.Many2one("account.account",string="Cuenta deudora int. anticip.",default= lambda self: self.env.company.asiento_interes_anti)
    asiento_antiguedad_anti_p=fields.Many2one("account.account",string="Cuenta acreedora anticip.",default= lambda self: self.env.company.asiento_antiguedad_anti_p)
    asiento_interes_anti_paga=fields.Many2one("account.account",string="Cuenta acreedora int. anticip.",default= lambda self: self.env.company.asiento_interes_anti_paga)


#Liquidación
    asiento_liq_int_pagar=fields.Many2one("account.account",default= lambda self: self.env.company.asiento_liq_int_pagar)
    asiento_liq_pag_pendi=fields.Many2one("account.account",default= lambda self: self.env.company.asiento_liq_pag_pendi)
    struct_liquidacion=fields.Many2one("hr.payroll.structure",string="Estructura Liquidación",default= lambda self: self.env.company.struct_liquidacion)
    struct_vacacion=fields.Many2one("hr.payroll.structure",string="Estructura Vacaciones Liq.",default= lambda self: self.env.company.struct_vacaciones)
       
    
    def configurar(self):


        compania=self.env.company
        compania.journal_for_prestaciones=self.journal_for_prestaciones
        compania.asiento_prestaciones=self.asiento_prestaciones
        compania.asiento_interes_pres=self.asiento_interes_pres
        compania.asiento_antiguedad_p=self.asiento_antiguedad_p
        compania.asiento_interes_paga=self.asiento_interes_paga

        compania.asiento_anticipo=self.asiento_anticipo
        compania.asiento_interes_anti=self.asiento_interes_anti
        compania.asiento_antiguedad_anti_p=self.asiento_antiguedad_anti_p
        compania.asiento_interes_anti_paga=self.asiento_interes_anti_paga

        compania.asiento_liq_int_pagar=self.asiento_liq_int_pagar
        compania.asiento_liq_pag_pendi=self.asiento_liq_pag_pendi
        compania.struct_liquidacion=self.struct_liquidacion
        compania.struct_vacaciones=self.struct_vacacion
        
