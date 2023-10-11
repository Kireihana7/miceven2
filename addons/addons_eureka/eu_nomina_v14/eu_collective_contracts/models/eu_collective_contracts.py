# -*- coding: utf-8 -*-

from datetime import datetime, timedelta,date
from odoo import models, fields,api
TODAY=datetime.today()
class EuCollectiveContract(models.Model):
    _name="hr.collective.contracts"
    _description="Contratos colectivos coño, ya lo escribi 5 veces"

    name=fields.Char("Nombre")
    active= fields.Boolean(string="Active",default="activo",tracking=True)
    company_id = fields.Many2one('res.company',string="Compañía", default=lambda self: self.env.company.id,tracking=True,invisible=True)
    currency_id = fields.Many2one("res.currency", string="Moneda",default=lambda self: self.company_id.currency_id)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Vigente'),
        ('cancelled', 'Cancelado'),
        ('terminated', 'Finalizado'),
    ],  default="draft", string="Estado",tracking=True)
    contract_ids=fields.One2many('hr.contract','parent_collect_contract_id',string="Contratos vinculados")
    fecha_consolidacion=fields.Date("Fecha de consolidación")
    fecha_terminacion=fields.Date("Fecha de terminación")


    additional_days_bonification=fields.Integer("Dias adicionales de bonificación")
    porcentaje_bonificacion_post_vacacional=fields.Float("% bonificación post vacacional")
    bono_cumplimiento=fields.Monetary("Bono por cumplimiento")
    bono_proteccion_social=fields.Monetary("Bono Prote. Social")
    bono_salud=fields.Monetary("Bono Salud")
    bono_capacitacion=fields.Monetary("Pago por Capacitación")
    bono_navidad=fields.Monetary("Bono por Navidad")


    additional_concepts=fields.One2many('hr.collective.additionals','parent_id',string="Conceptos adicionales")

    def post(self):
        for rec in self:
            rec.state='posted'
            rec.fecha_consolidacion=TODAY

    def to_draft(self):
        for rec in self:
            rec.state='draft'
            rec.fecha_consolidacion=False

    def cancel(self):
        for rec in self:
            rec.state='cancelled'
            rec.fecha_consolidacion=False
    def terminated(self):
        for rec in self:
            rec.state='terminated'
            rec.fecha_terminacion=TODAY

class EuCollectiveAdditonals(models.Model):
    _name="hr.collective.additionals"
    _description="Contratos colectivos coño, ya lo escribi 5 veces"

    parent_id=fields.Many2one('hr.collective.contracts',string="Colectivo")
    concepto=fields.Char('Concepto')
    valor=fields.Float('Valor')
