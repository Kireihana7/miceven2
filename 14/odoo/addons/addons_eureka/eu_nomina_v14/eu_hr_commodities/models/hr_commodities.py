# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from datetime import datetime,date
from dateutil import relativedelta


class HrCommodities(models.Model):
    _name="hr.commodities"
    _inherit=['mail.thread', 'mail.activity.mixin']
    _description="Tabla de comodidades de los empleados"


    active=fields.Boolean("Activo",default=True)
    state=fields.Selection([('draft','Sin autorizar'),('posted','Autorizado')],default="draft")
    name=fields.Char("Nombre",tracking=True)
    type=fields.Selection([('digital','Digital'),('machine','Maquinaria'),
                            ('clothing','Vestimenta'),('document','Documentos'),
                            ('chemical','Químicos'),('tool','Herramientas'),
                            ('transport','Transporte'),('animal','Animales'),('other','Otros')
                            ],string="Tipo de comodidad",required=True,tracking=True)
    analitic_account=fields.Many2one('account.analytic.account',string="Centro de costo",tracking=True)
    description=fields.Char("Descripción",tracking=True)
    serial=fields.Char("Número o Serial")
    brand_model=fields.Char("Marca")
    image_256=fields.Image(string="imagen ilustrativa",max_width=256, max_height=256,tracking=True)
    in_use=fields.Boolean(string="En uso",tracking=True,compute="_compute_asignates")
    asignament_count=fields.Integer(string="numero asignados",tracking=True,compute="_compute_asignates")
    
    def autorize_unatorized(self):
        for rec in self:
            if rec.state=="draft":
                rec.state="posted"
            else:
                rec.state="draft"
    def _compute_asignates(self):
        for rec in self:
            asigns=self.env['hr.employee'].search([('commodities','!=',False)]).filtered(lambda x: rec in x.commodities)
            if len(asigns)>0:
                rec.in_use=True
                rec.asignament_count=len(asigns)
            else:
                rec.in_use=False
                rec.asignament_count=0


    def go_to_asignates(self):
        for rec in self:
            asigns=self.env['hr.employee'].search([('commodities','!=',False)]).filtered(lambda x: rec in x.commodities)
            ids=[]
            if asigns:
                ids=asigns.ids
            return {
            'type':'ir.actions.act_window',
            'name': f'Asignados para {rec.name}',
            'res_model':'hr.employee',
            'domain':[('id','in',ids)],
            'view_mode':'tree',
            'target':'current',
            'context':{'no_create':True}
        }

