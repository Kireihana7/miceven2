
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
class ResCompany(models.Model):

    _inherit = 'res.company'

# diario base para prestaciones corporativas
    journal_for_prestaciones_corporate=fields.Many2one("account.journal",tracking=True)

#Prestacion
    asiento_prestaciones_corporate=fields.Many2one("account.account",string="Cuenta deudora prest.",tracking=True)
    asiento_interes_pres_corporate=fields.Many2one("account.account",string="Cuenta deudora int. prest.",tracking=True)
    asiento_antiguedad_p_corporate=fields.Many2one("account.account",string="Cuenta acreedora prest.",tracking=True)
    asiento_interes_paga_corporate=fields.Many2one("account.account",string="Cuenta acreedora int. prest.",tracking=True)
#Anticipo
    asiento_anticipo_corporate=fields.Many2one("account.account",string="Cuenta deudora anticip.",tracking=True)
    asiento_interes_anti_corporate=fields.Many2one("account.account",string="Cuenta deudora int. anticip.",tracking=True)
    asiento_antiguedad_anti_p_corporate=fields.Many2one("account.account",string="Cuenta acreedora anticip.",tracking=True)
    asiento_interes_anti_paga_corporate=fields.Many2one("account.account",string="Cuenta acreedora int. anticip.",tracking=True)

#Vacaciones y liquidaciones

    asiento_liq_int_pagar_corporate=fields.Many2one("account.account",tracking=True)
    asiento_liq_pag_pendi_corporate=fields.Many2one("account.account",tracking=True)
    struct_liquidacion_corporate=fields.Many2one("hr.payroll.structure",string="Estructura Liquidación",tracking=True)
    struct_vacacion_corporate=fields.Many2one("hr.payroll.structure",string="Estructura Vacaciones Liq.",tracking=True)
    