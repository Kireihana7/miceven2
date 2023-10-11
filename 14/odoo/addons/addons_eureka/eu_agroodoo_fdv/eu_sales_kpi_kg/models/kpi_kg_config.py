# -*- coding: utf-8 -*-

from calendar import monthrange
from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

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

class KpiKgConfig(models.Model):
    _name = "kpi.kg.config"
    _description = "Configuración del KPI por kilogramo"
    _inherit = 'kpi.mixin'

    name = fields.Char("Nombre", tracking=True,)
    status = fields.Selection([
        ("planning", "Planificando"),
        ("active", "Activo"),
        ("expired", "Expirado"),
    ], "Estatus", default="planning", tracking=True)

    # Meta
    kpi_branch_ids = fields.One2many("kpi.config.branch", "kpi_kg_config_id", "Sucursales", tracking=True,)
    kpi_categ_ids = fields.One2many("kpi.config.category.group", "kpi_kg_config_id", "Categorias", tracking=True,)
    kpi_salesperson_id = fields.One2many("kpi.config.salesperson","kpi_kg_config_id",tracking=True,)
    kpi_salesperson_category_id = fields.One2many('kpi.salesperson.category','kpi_kg_config_id',string="Categorías",tracking=True,)
    kpi_branch_category_id = fields.One2many('kpi.branch.category','kpi_kg_config_id',string="Distribución",tracking=True,)
    pricelist_id = fields.Many2one("product.pricelist", "Lista de precio",tracking=True,)
    kpi_tabla = fields.Many2one('kpi.tabla',string="Objetivos del Mes",tracking=True,required=True)
    # Time
    month = fields.Selection(list(MONTHS.items()), "Mes", default=lambda self: str(fields.Date.today().month), tracking=True,)
    year = fields.Integer("Año", default=lambda self: fields.Date.today().year, tracking=True,)
    start_date = fields.Date("Fecha de inicio", compute="_compute_dates", tracking=True, store=True)
    end_date = fields.Date("Fecha de culminación", compute="_compute_dates", tracking=True, store=True)
    salesperson_count = fields.Integer("Vendedores", compute='_compute_salesperson_count', store=True)
    branch_count = fields.Integer("Sucursales", compute='_compute_branch_count', store=True)
    category_count = fields.Integer("Categorías", compute='_compute_category_count', store=True)
    salesperson_goal = fields.Float(
        "Meta distribuida vendedores",
        compute="_compute_salesperson_goal",
        tracking=True,
        store=True,
    )

    #region Properties
    @property
    def date_range(self):
        return {
            "start": str(self.start_date) if self.start_date else None,
            "end": str(self.end_date) if self.end_date else None,
        }

    @property
    def date_fields(self) -> dict:
        self.ensure_one()

        year, month = list(map(int, [self.year, self.month]))

        if not any([year, month]):
            return {}

        return {
            "month": month,
            "year": year,
        }
    #endregion

    @api.model
    def create(self, vals_list):
        gerente_id = self.env['ir.config_parameter'] \
            .sudo() \
            .get_param('eu_sales_kpi_kg.national_manager')

        if not gerente_id:
            raise UserError("No hay un gerente nacional definido")

        res = super().create(vals_list)

        for rec in res:
            rec.kpi_salesperson_id.create({
                "salesperson_id": int(gerente_id),
                "rank": "gerente_nacional",
                "kpi_kg_config_id": rec.id,
            })

        return res
        
    @api.onchange("year", "month")
    def _onchange_month_and_year(self):
        for rec in self:
            dates = self.date_fields

            if not dates:
                continue

            rec.name = "KPI de {month} {year}".format(month=MONTHS[str(dates["month"])], year=dates["year"])
 
    @api.constrains("kpi_categ_ids")
    def _check_kpi_categ_ids(self):
        for rec in self:
            categ_ids = [set(categ.categ_ids.ids) for categ in rec.kpi_categ_ids]
            if sum(rec.kpi_categ_ids.mapped('weight_percent'))> 100:
                raise ValidationError('El Peso % no puede ser mayora 100%')

            while categ_ids:
                current_ids = categ_ids.pop()

                if any(current_ids & categ for categ in categ_ids):
                    raise ValidationError("Las categorias no se pueden repetir")

    #region Computes
    @api.depends("kpi_branch_ids.goal")
    def _compute_distributed_goal(self):
        for rec in self:
            rec.distributed_goal = sum(rec.kpi_branch_ids.mapped("goal"))

    @api.depends("kpi_salesperson_id.goal","kpi_salesperson_id.rank")
    def _compute_salesperson_goal(self):
        for rec in self:
            rec.salesperson_goal = sum(rec.kpi_salesperson_id.filtered(lambda x: x.rank == 'vendedor').mapped("goal"))

    @api.depends("kpi_branch_ids.progress")
    def _compute_progress(self):
        for rec in self:
            rec.progress = sum(rec.kpi_branch_ids.mapped("progress"))

    @api.depends("year", "month")
    def _compute_dates(self):
        for rec in self:
            dates = rec.date_fields

            if not dates:
                rec.start_date = rec.end_date = None
                
                continue
            
            year = dates["year"]
            month = dates["month"]
            
            last_day = monthrange(year, month)[1]

            rec.start_date = date(year, month, day=1)
            rec.end_date = date(year, month, day=last_day)

    @api.depends("kpi_salesperson_id")
    def _compute_salesperson_count(self):
        for rec in self:
            rec.salesperson_count = len(rec.kpi_salesperson_id)

    @api.depends("kpi_branch_ids")            
    def _compute_branch_count(self):
        for rec in self:
            rec.branch_count = len(rec.kpi_branch_ids)

    @api.depends("kpi_salesperson_category_id")            
    def _compute_category_count(self):
        for rec in self:
            rec.category_count = len(rec.kpi_salesperson_category_id)
    #endregion

    #region Actions
    def action_compute_everything(self):
        salesperson = self.kpi_salesperson_id
        category = self.kpi_salesperson_category_id

        salesperson._compute_devoluciones()
        salesperson._compute_progress()
        category._compute_progress()
        category._compute_logro()
        category._compute_kpi_percent()
        
    def action_show_salesperson_id(self):
        self.ensure_one()

        res = self.env.ref('eu_sales_kpi_kg.kpi_config_salesperson_action')
        res = res.read()[0]
        res['domain'] = str([('kpi_kg_config_id', '=', self.id)])
        res['context'] = {'create': False}
        return res

    def action_show_branch_ids(self):
        self.ensure_one()

        res = self.env.ref('eu_sales_kpi_kg.kpi_config_branch_action')
        res = res.read()[0]
        res['domain'] = str([('kpi_kg_config_id', '=', self.id)])
        res['context'] = {'create': False}
        return res

    def action_show_category_id(self):
        self.ensure_one()

        res = self.env.ref('eu_sales_kpi_kg.kpi_config_category_action')
        res = res.read()[0]
        res['domain'] = str([('kpi_kg_config_id', '=', self.id)])
        res['context'] = {'create': False,'delete': False,'edit': False}
        return res
    #endregion