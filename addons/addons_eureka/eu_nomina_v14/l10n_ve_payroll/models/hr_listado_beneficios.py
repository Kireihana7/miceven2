from math import floor
from odoo.exceptions import UserError,ValidationError
from odoo import models, fields,api
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta,date
from calendar import monthrange
TODAY=date.today()

class HRlistBeneficios(models.Model):
    _name = 'hr.list.beneficios'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char("Nombre asignado",tracking=True)
    code=fields.Char("Código Corto",required=True,tracking=True)
    date_start=fields.Date("Fecha de Inicio",tracking=True)
    date_end=fields.Date("Fecha de Final",tracking=True)
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company.id,tracking=True,invisible=True)

    beneficios=fields.One2many("list.beneficios.line","parent_id","Beneficios del periodo",tracking=True)
    incomplete_product=fields.Boolean("")

    @api.onchange("beneficios")
    def onchange_beneficios(self):
        for rec in self:
            if rec.beneficios.filtered(lambda x: x.existence==0):
                rec.incomplete_product=True
            else:
                rec.incomplete_product=False

class HRlistBeneficiosLine(models.Model):
    _name = 'list.beneficios.line'

    parent_id=fields.Many2one("hr.list.beneficios")
    type_of_right=fields.Selection([('inherent','inalienable'),('puntual','Por puntualidad'),('exemplar','Por trab. ejemplar')],string="Tipo de beneficio",required=True)
    producto_id=fields.Many2one("product.product","Producto o beneficio",required=True)
    existence=fields.Float(related="producto_id.qty_available")
    product_quantity=fields.Integer("Cantidad")


