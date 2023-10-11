from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrConfigPrestacionCWiz(models.TransientModel):
    _name = 'hr.config.prestacion.c.wiz'
    
    journal_for_prestaciones_corporate=fields.Many2one("account.journal",tracking=True,default=lambda self: self.env.company.journal_for_prestaciones_corporate)

#Prestacion
    asiento_prestaciones_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_prestaciones_corporate)
    asiento_interes_pres_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_interes_pres_corporate)
    asiento_antiguedad_p_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_antiguedad_p_corporate)
    asiento_interes_paga_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_interes_paga_corporate)
#Anticipo
    asiento_anticipo_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_anticipo_corporate)
    asiento_interes_anti_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_interes_anti_corporate)
    asiento_antiguedad_anti_p_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_antiguedad_anti_p_corporate)
    asiento_interes_anti_paga_corporate=fields.Many2one("account.account",tracking=True,default=lambda self: self.env.company.asiento_interes_anti_paga_corporate)
    
    
# Liquidaciones y vacaciones
    asiento_liq_int_pagar_corporate=fields.Many2one("account.account",default= lambda self: self.env.company.asiento_liq_int_pagar_corporate)
    asiento_liq_pag_pendi_corporate=fields.Many2one("account.account",default= lambda self: self.env.company.asiento_liq_pag_pendi_corporate)
    struct_liquidacion_corporate=fields.Many2one("hr.payroll.structure",default= lambda self: self.env.company.struct_liquidacion_corporate)
    struct_vacacion_corporate=fields.Many2one("hr.payroll.structure",default= lambda self: self.env.company.struct_vacacion_corporate)
    
    def configurar(self):
        compania=self.env.company
        
        if self.asiento_liq_int_pagar_corporate:

            compania.asiento_liq_int_pagar_corporate=self.asiento_liq_int_pagar_corporate
        
        if self.asiento_liq_pag_pendi_corporate:

            compania.asiento_liq_pag_pendi_corporate=self.asiento_liq_pag_pendi_corporate

        if self.struct_liquidacion_corporate:

            compania.struct_liquidacion_corporate=self.struct_liquidacion_corporate

        if self.struct_vacacion_corporate:

            compania.struct_vacacion_corporate=self.struct_vacacion_corporate

        #
        if self.journal_for_prestaciones_corporate:

            compania.journal_for_prestaciones_corporate=self.journal_for_prestaciones_corporate
        
        if self.asiento_prestaciones_corporate:

            compania.asiento_prestaciones_corporate=self.asiento_prestaciones_corporate
        
        if self.asiento_interes_pres_corporate:

            compania.asiento_interes_pres_corporate=self.asiento_interes_pres_corporate

        if self.asiento_antiguedad_p_corporate:

            compania.asiento_antiguedad_p_corporate=self.asiento_antiguedad_p_corporate
        
        if self.asiento_interes_paga_corporate:

            compania.asiento_interes_paga_corporate=self.asiento_interes_paga_corporate
        
        if self.asiento_anticipo_corporate:

            compania.asiento_anticipo_corporate=self.asiento_anticipo_corporate
        
        if self.asiento_interes_anti_corporate:

            compania.asiento_interes_anti_corporate=self.asiento_interes_anti_corporate
        
        if self.asiento_antiguedad_anti_p_corporate:

            compania.asiento_antiguedad_anti_p_corporate=self.asiento_antiguedad_anti_p_corporate
        
        if self.asiento_interes_anti_paga_corporate:

            compania.asiento_interes_anti_paga_corporate=self.asiento_interes_anti_paga_corporate


                       