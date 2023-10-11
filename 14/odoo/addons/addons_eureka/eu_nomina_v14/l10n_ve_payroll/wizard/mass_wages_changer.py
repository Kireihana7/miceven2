from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
TODAY = date.today()
class HrMassContractChanger(models.TransientModel):
    _name = 'hr.mass.contract.changer.wizard'
    _description="Renueva los ocntratos y los cambia a indefinidos si pasa de dos"


    selector=fields.Selection([('porcentaje','Porcentaje'),('monto','Monto fijo'),('sustitucion','Sustituir')],string="modo de aumento",required=True)
    wage_fixed=fields.Float(string="Aumento del salario base")
    complemento_fixed=fields.Float(string="Aumento del complemento")
    cesta_ticket_fixed=fields.Float(string="Aumento del Cesta Ticket")
    wage_perc=fields.Float(string="Aumento del salario base %")
    complemento_perc=fields.Float(string="Aumento del complemento %")
    cesta_ticket_perc=fields.Float(string="Aumento del Cesta Ticket %")
    wage_sus=fields.Float(string="Sustitución del salario base ")
    complemento_sus=fields.Float(string="Sustitución del complemento ")
    cesta_ticket_sus=fields.Float(string="Sustitución del Cesta Ticket ")

    @api.onchange('selector')
    def onchange_selector(self):
        for rec in self:
            if rec.selector=="porcentaje":
                rec.wage_fixed=0
                rec.complemento_fixed=0
                rec.cesta_ticket_fixed=0
                rec.wage_sus=0
                rec.complemento_sus=0
                rec.cesta_ticket_sus=0
            elif rec.selector=="monto":
                rec.wage_perc=0
                rec.complemento_perc=0
                rec.cesta_ticket_perc=0
                rec.wage_sus=0
                rec.complemento_sus=0
                rec.cesta_ticket_sus=0
            else:
                rec.wage_perc=0
                rec.complemento_perc=0
                rec.cesta_ticket_perc=0
                rec.wage_fixed=0
                rec.complemento_fixed=0
                rec.cesta_ticket_fixed=0

    def update(self):
        for rec in self:
            active_ids = self._context.get('active_ids') or self._context.get('active_id')
            active_model = self._context.get('active_model') 

            targets=self.env[active_model].browse(active_ids)
            if rec.selector=="porcentaje":

                for target in targets:
                    if rec.wage_perc>0:
                        target.wage= target.wage*(1+(rec.wage_perc/100))
                        target._onchange_wage_to_history()
                    if rec.complemento_perc>0:
                        target.complemento= target.complemento*(1+(rec.complemento_perc/100))
                        target._onchange_complemento_to_history()
                    if rec.cesta_ticket_perc>0:
                        target.cesta_ticket= target.cesta_ticket*(1+(rec.cesta_ticket_perc/100))
                        target._onchange_cesta_ticket_to_history()
            elif rec.selector=="monto":
                for target in targets:
                    if rec.wage_fixed>0:
                        target.wage= target.wage+rec.wage_fixed
                        target._onchange_wage_to_history()
                    if rec.complemento_fixed>0:
                        target.complemento= target.complemento+rec.complemento_fixed
                        target._onchange_complemento_to_history()
                    if rec.cesta_ticket_fixed>0:
                        target.cesta_ticket= target.cesta_ticket+rec.cesta_ticket_fixed
                        target._onchange_cesta_ticket_to_history()
            else:
                for target in targets:
                    if rec.wage_sus>0:
                        target.wage= rec.wage_sus
                        target._onchange_wage_to_history()
                    if rec.complemento_sus>0:
                        target.complemento=rec.complemento_sus
                        target._onchange_complemento_to_history()
                    if rec.cesta_ticket_sus>0:
                        target.cesta_ticket= rec.cesta_ticket_sus
                        target._onchange_cesta_ticket_to_history()


