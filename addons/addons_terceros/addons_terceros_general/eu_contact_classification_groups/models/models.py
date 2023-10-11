# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class ClassificationPartnerTable(models.Model):
    _name = 'class.partner.table'
    _inherit=['mail.thread', 'mail.activity.mixin']
    _description = 'Tabla de clasificacion de contactos'

    name = fields.Char('Titulo',tracking=True)
    usual_type=fields.Selection([('client','Cliente'),('provider','Proveedor')],string="Tipo usual de miembros",help="El tipo usual de los contactos que son agregados",tracking=True)
    state=fields.Selection([('draft','Borrador'),('open','Abierta'),('close','Cerrada'),('cancel','Anulada')],default="draft",string='Estado',tracking=True)
    # type_class=fields.Selection([('client','Cliente'),('provider','Proveedor')],default="client",string="Tipo de Asociación")
    client_partners_id = fields.One2many('res.partner','client_agroupation',string="Contactos como clientes",tracking=True)
    provider_partners_id = fields.One2many('res.partner','provider_agroupation',string="Contactos como Proveedores",tracking=True)
    description = fields.Text('Descripción',tracking=True)


    def button_return_draft(self):
        for rec in self:
            rec.state="draft"

    def button_cancel(self):
        for rec in self:
            rec.state="cancel"

    def button_open_close(self):
        for rec in self:
            if rec.state=="open":
                rec.state="close"
            elif rec.state in ["close","draft"]:
                rec.state="open"
            else:
                raise UserError("No puede alterar una clasificación cancelada")

    def unlink(self):
        for rec in self:
            if rec.state!='cancel':
                raise UserError("No puedes eliminar una Clasificación que no este en borrador")
