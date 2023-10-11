# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

MONTHS = {
    "1": "Enero",
    "2": "Febrero",
    "3": "Marzo",
    "4": "Abril",
    "5": "Mayo",
    "6": "Junio",
    "7": "Julio",
    "8": "Agosto",
    "9": "Septiembre",
    "10": "Octubre",
    "11": "Noviembre",
    "12": "Diciembre",
}

years_range = list(range(2020, 2041))

YEARS = dict(zip(map(str, years_range), years_range))

class KpiTabla(models.Model):
    _name = "kpi.tabla"
    _description = "Parametrización KPI"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Descripción de los Objetivos",tracking=True)
    month = fields.Selection(list(MONTHS.items()), "Mes", default=lambda self: str(fields.Date.today().month), tracking=True,required=True)
    year = fields.Selection(list(YEARS.items()), "Año", default=lambda self: str(fields.Date.today().year), tracking=True,required=True)
    line_ids = fields.One2many('kpi.tabla.distribucion','tabla_id',string="Líneas de Cobertura")
    
    salesman_bonification = fields.Float("Bonificación de vendedor",tracking=True)
    manager_bonification = fields.Float("Bonificación del coordinador",tracking=True)
    branch_manager_bonification = fields.Float("Bonificación del gerente de sucursal",tracking=True)
    national_manager_bonification = fields.Float("Bonificación del gerente nacional",tracking=True)

    volumen_min = fields.Float("Volumen % Min",tracking=True)
    cobranza_min = fields.Float("Cobranza Uno % Min",tracking=True)
    cobranza_dos_min = fields.Float("Cobranza Dos % Min",tracking=True)
    precio_promedio_min = fields.Float("Precio Promedio % Min",tracking=True)
    activacion_min = fields.Float("Activación Min",tracking=True)

    volumen_max = fields.Float("Volumen % Max",tracking=True)
    cobranza_max = fields.Float("Cobranza Uno % Max",tracking=True)
    cobranza_dos_max = fields.Float("Cobranza Dos % Max",tracking=True)
    precio_promedio_max = fields.Float("Precio Promedio % Max",tracking=True)
    activacion_max = fields.Float("Activación Max",tracking=True)
    variante_cobranza_dos = fields.Float("Variante Cobranza Dos",tracking=True)
    state = fields.Selection([
        ('inactivo', 'Inactivo'),
        ('activo', 'Activo'),
    ], string='Estatus', readonly=True, copy=False, index=True, tracking=True, default='inactivo')

    def action_set_activar(self):
        for rec in self:
            if self.env['kpi.tabla'].search_count([
                ('id','!=',rec.id),
                ('month','=',rec.month),
                ('year','=',rec.year),
            ]):
                raise UserError('Ya existe un objetivo para esta fecha')

        
        self.write({"state": "activo"})

    #region Constrains
    @api.constrains("total")
    def _check_total(self):
        for rec in self:
            if rec.total > 100:
                raise ValidationError("El total no puede ser mayor a 100%")

    @api.constrains('line_ids')
    def _check_exist_line_ids(self):
        for rec in self:
            numbers: list[int] = rec.line_ids.mapped("numero")

            for n in set(numbers):
                if numbers.count(n) > 1:
                    raise ValidationError(_(f"No puede repetirse el número de Familias - {n}"))
    #endregion

class KpiTablaDistribucion(models.Model):
    _name = "kpi.tabla.distribucion"
    _description = "Distribucion KPI"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    tabla_id = fields.Many2one('kpi.tabla',string="Parametrización KPI")
    name = fields.Char("Nombre", related="tabla_id.name")
    numero = fields.Integer("Cant. Familia Activada")
    volumen = fields.Float("Volumen %",tracking=True)
    cobranza = fields.Float("Cobranza Uno %",tracking=True)
    cobranza_dos = fields.Float("Cobranza Dos %",tracking=True)
    precio_promedio = fields.Float("Precio Promedio %",tracking=True)
    activacion = fields.Float("Activación %",tracking=True)
    total = fields.Float("Total %",compute="_compute_total",tracking=True,store=True)

    @api.depends('volumen','cobranza','precio_promedio','activacion','cobranza_dos')
    def _compute_total(self):
        for rec in self:
            rec.total = sum([rec.volumen, rec.cobranza, rec.cobranza_dos, rec.precio_promedio, rec.activacion])