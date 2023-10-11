# -*- coding: utf-8 -*-

from datetime import date,datetime
from typing import List
from odoo import models, fields, api
from odoo.exceptions import UserError

class KpiConfigSalesperson(models.Model):
    _name = "kpi.config.salesperson"
    _description = "Vendedores de KPI"
    _inherit = 'kpi.mixin'

    name = fields.Char("Nombre", related="salesperson_id.name", tracking=True,)
    salesperson_id = fields.Many2one("hr.employee", "Vendedor", tracking=True, ondelete="restrict")
    rank = fields.Selection([
        ("vendedor", "Vendedor"),
        ("coordinador", "Coordinador"),
        ("gerente_sucursal", "Gerente de sucursal"),
        ("gerente_nacional", "Gerente nacional"),
    ], "Posición", tracking=True)
    crm_team_id = fields.Many2one("crm.team", "Equipo de venta", tracking=True)
    parent_id = fields.Many2one("kpi.config.salesperson", "Superior", tracking=True)
    kpi_branch_id = fields.Many2one("kpi.config.branch", "Sucursal", ondelete="cascade", tracking=True,)
    kpi_subcategory_ids = fields.One2many("kpi.salesperson.category", "kpi_salesperson_id", "Categorias", tracking=True)
    kpi_kg_config_id = fields.Many2one("kpi.kg.config", "KPI", ondelete="cascade")
    status = fields.Selection(related="kpi_kg_config_id.status",tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    category_active = fields.Integer(string="Categorías Activadas",compute="_compute_category_active")
    progress_percent = fields.Float(string="Progreso %",compute="_compute_progress_percent")
    goal = fields.Float("Meta", tracking=True,digits=(10,2))
    # Precio Promedio
    goal_average_price = fields.Monetary("Meta P.P", tracking=True)
    average_price = fields.Monetary("Precio promedio", compute="_compute_progress", tracking=True)
    logro_average_price = fields.Float(string="Logro P.P %",compute="_compute_logro_average_price",tracking=True)
    kpi_percent_pp = fields.Float(string="KPI P.P %",compute="_compute_activaciones",tracking=True)
    kpi_amount_pp = fields.Float(string="Valor P.P",compute="_compute_logro_average_price",tracking=True)
    kpi_bono_pp = fields.Float(string="Bono P.P",compute="_compute_logro_average_price",tracking=True)

    # Activación
    customers_to_active = fields.Integer("Clientes para activación", tracking=True)
    customer_active = fields.Integer('Clientes Activados',compute="_compute_activacion",tracking=True)
    is_active = fields.Boolean("Activo", compute="_compute_progress", tracking=True)
    logro_ac = fields.Float(string="Logro Activación %",compute="_compute_activacion",tracking=True)
    kpi_percent_ac = fields.Float(string="KPI Activación %",compute="_compute_activaciones",tracking=True)
    kpi_amount_ac = fields.Float(string="Valor Activación",compute="_compute_activacion",tracking=True)
    kpi_bono_ac = fields.Float(string="Bono Activación",compute="_compute_activacion",tracking=True)
    
    # Volumen
    actual_percent = fields.Float(string="Logro Volumen %",compute="_compute_logro",tracking=True)
    
    # Cobranza
    xcobrar_pasado = fields.Float(string='CxC Mes Pasado',compute="_compute_xcobrar_pasado",tracking=True)
    xcobrar_mes = fields.Float(string='Cobranza',compute="_compute_xcobrar_mes",tracking=True)
    logro_cobranza = fields.Float(string="Logro Cobranza %",compute="_compute_meta_cobranza",tracking=True)
    kpi_percent_cc = fields.Float(string="KPI Cobranza %",compute="_compute_activaciones",tracking=True)
    meta_cobranza = fields.Float(string="Meta Cobranza",compute="_compute_meta_cobranza",tracking=True)
    kpi_amount_cc = fields.Float(string="Valor Cobranza",compute="_compute_meta_cobranza",tracking=True)
    kpi_bono_cc = fields.Float(string="Bono Cobranza",compute="_compute_meta_cobranza",tracking=True)

    #Cobranza 2
    xcobrar_vencidas = fields.Float(string="Cxc Vencidas",compute="_compute_meta_cobranza_dos",tracking=True)
    xcobrar_no_vencidas = fields.Float(string="Cxc No Vencidas",compute="_compute_meta_cobranza_dos",tracking=True)
    kpi_logro_cc_dos = fields.Float(string="Logro Cobranza Dos %",compute="_compute_meta_cobranza_dos",tracking=True)
    kpi_percent_cc_dos = fields.Float(string="KPI Cobranza Dos %",compute="_compute_activaciones",tracking=True)
    meta_cobranza_dos = fields.Float(string="Meta Cobranza Dos",compute="_compute_meta_cobranza_dos",tracking=True)
    kpi_amount_cc_dos = fields.Float(string="Valor Cobranza Dos",compute="_compute_meta_cobranza_dos",tracking=True)
    kpi_bono_cc_dos = fields.Float(string="Bono Cobranza Dos",compute="_compute_meta_cobranza_dos",tracking=True)

    # Total Bono
    total_bono = fields.Float(string="Total Bono",compute="_compute_total_bono",tracking=True)
    
    devoluciones = fields.Float("Devoluciones", compute="_compute_devoluciones", tracking=True,)
    venta_mes = fields.Float("Venta del Mes", compute="_compute_venta_mes", tracking=True,)

    bonification = fields.Float("Bonificación", compute="_compute_bonification",tracking=True)

    def get_invoice_domain_by_rank(self) -> List[tuple]:
        #self.ensure_one()
        domain = []
        if self.salesperson_id:
            if self.salesperson_id.branch_id:
                branch_id = self.salesperson_id.branch_id.id
                domain.append(("branch_id", "=", branch_id))
            invoice_user_ids = None
            
            if self.rank == "vendedor":
                domain.append(("invoice_user_id", "=", self.salesperson_id.user_id.id))
            
            if self.rank == "coordinador":
                invoice_user_ids = self.with_context(active_test=False).crm_team_id.user_id + self.with_context(active_test=False).crm_team_id.member_ids
            
            if self.rank == "gerente_sucursal":
                invoice_user_ids = self.env["crm.team"].with_context(active_test=False) \
                    .search([("branch_id", "=", branch_id)]) \
                    .mapped(lambda t: t.user_id + t.member_ids)
            
            if invoice_user_ids:
                domain.append(("invoice_user_id", "in", invoice_user_ids.ids))
            return domain
        else:
            return domain


    # El constrains del abstracto no funciona
    #region Onchanges
    @api.onchange("distributed_goal", "goal")
    def _onchange_goals(self):
        for rec in self:
            if round(rec.distributed_goal,2) > round(rec.goal,2):
                raise UserError(("La meta distribuida no puede ser mayor a la meta, DistributedGoal: %s, Goal: %s") % (rec.distributed_goal,rec.goal))

    @api.onchange("rank")
    def _onchange_rank(self):
        self.update({
            "kpi_branch_id": None,
            "parent_id": None,
            "crm_team_id": None,
        })

    @api.onchange("crm_team_id")
    def _onchange_crm_team_id(self):
        for rec in self:
            team = rec.crm_team_id.with_context(active_test=False)
            if team and (rec.salesperson_id.user_id not in (team.user_id + team.member_ids)):
                raise UserError("El usua")
    #endregion

    #region Computes
    @api.depends(
        "rank",
        "parent_id",
        "kpi_kg_config_id.kpi_tabla.salesman_bonification",
        "kpi_kg_config_id.kpi_tabla.manager_bonification",
        "kpi_kg_config_id.kpi_tabla.branch_manager_bonification",
        "kpi_kg_config_id.kpi_tabla.national_manager_bonification",
    )
    def _compute_bonification(self):
        for rec in self:
            if rec.rank == "vendedor":
                rec.bonification = rec.kpi_kg_config_id.kpi_tabla.salesman_bonification
            elif rec.rank == "coordinador":
                rec.bonification = rec.kpi_kg_config_id.kpi_tabla.manager_bonification
            elif rec.rank == "gerente_sucursal":
                rec.bonification = rec.kpi_kg_config_id.kpi_tabla.branch_manager_bonification
            else:
                rec.bonification = rec.kpi_kg_config_id.kpi_tabla.national_manager_bonification

    @api.depends("kpi_subcategory_ids.goal")
    def _compute_distributed_goal(self):
        for rec in self:
            rec.distributed_goal = sum(rec.kpi_subcategory_ids.mapped("goal"))

    @api.depends(
        "rank",
        "salesperson_id.user_id",
        "kpi_kg_config_id.start_date",
        "kpi_kg_config_id.end_date",
        "salesperson_id.user_id.partner_id.invoice_ids.move_type",
        "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_date",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.quantity",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
        "crm_team_id.user_id",
        "crm_team_id.member_ids",
        "salesperson_id.branch_id",
        "salesperson_id.branch_id.crm_team_ids.user_id",
        "salesperson_id.branch_id.crm_team_ids.member_ids",
        "parent_id",
    )    
    def _compute_devoluciones(self):
        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range

            domain = [
                ("move_type", "=", "out_refund"),
                ("state", "=", "posted"),
                ("parent_id.invoice_date", "<=", dates["start"]),
                ("invoice_date", ">=", dates["start"]),
                ("invoice_date", "<=", dates["end"]),
            ]
            if rec.rank !='gerente_nacional':
                domain += rec.get_invoice_domain_by_rank()

            line_ids = self.env["account.move"].sudo() \
                .search(domain) \
                .mapped("invoice_line_ids")

            rec.devoluciones = sum(line_ids.mapped(lambda l: l.product_id.weight * l.quantity))
            
    @api.depends("devoluciones", "progress")            
    def _compute_venta_mes(self):
        for rec in self:
            rec.venta_mes = rec.progress + rec.devoluciones
            
    @api.depends(
        "rank",
        "parent_id",
        "devoluciones",
        "goal_average_price",
        "customers_to_active",
        "kpi_kg_config_id.start_date",
        "kpi_kg_config_id.end_date",
        "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.quantity",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.price_subtotal",
        "salesperson_id.user_id.partner_id.invoice_ids.partner_id",
        "salesperson_id.user_id.partner_id.invoice_ids.move_type",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_date",
        "crm_team_id.user_id",
        "crm_team_id.member_ids",
        "salesperson_id.branch_id",
        "salesperson_id.branch_id.crm_team_ids.user_id",
        "salesperson_id.branch_id.crm_team_ids.member_ids",
    )
    def _compute_progress(self):
        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range

            domain = [
                ("state", "=", "posted"),
                ("invoice_date", ">=", dates["start"]),
                ("invoice_date", "<=", dates["end"]),
            ]
            if rec.rank !='gerente_nacional':
                domain += rec.get_invoice_domain_by_rank()

            move_ids = self.env["account.move"].sudo() \
                .search([
                    *domain,
                    ("move_type", "=", "out_invoice"),
                ])

            move_ids_refund = self.env["account.move"].sudo() \
                .search([
                    *domain,
                    ("move_type", "=", "out_refund"),
                    ("parent_id.invoice_date", ">=", dates["start"]),
                    ("parent_id.invoice_date", "<=", dates["end"]),
                ]) \
                .mapped("invoice_line_ids") \
                .mapped(lambda l: l.product_id.weight * l.quantity)

            move_ids_refund = sum(move_ids_refund or [])

            if not move_ids:
                rec.average_price = rec.progress = 0
                rec.is_active = False

                continue

            invoice_lines = move_ids.mapped("invoice_line_ids")

            rec.progress = sum(invoice_lines.mapped(lambda l: l.product_id.weight * l.quantity)) - move_ids_refund - rec.devoluciones
            rec.is_active = len(move_ids.mapped("partner_id")) >= rec.customers_to_active

            prices = sum(invoice_lines.mapped('price_subtotal'))
            peso = sum(invoice_lines.mapped('weight_total'))

            #raise UserError(sum(prices))
            rec.average_price = prices / peso

    @api.depends(
        'kpi_subcategory_ids.actual_percent', 
        "kpi_subcategory_ids.kpi_kg_config_id.kpi_tabla.volumen_min"
    )
    def _compute_category_active(self):
        for rec in self:
            rec.category_active = len(rec.kpi_subcategory_ids.filtered(lambda x: x.actual_percent > x.kpi_kg_config_id.kpi_tabla.volumen_min))

    @api.depends(
        'category_active',
        'kpi_kg_config_id.kpi_tabla.line_ids.numero',
        "kpi_kg_config_id.kpi_tabla.line_ids.precio_promedio",
        "kpi_kg_config_id.kpi_tabla.line_ids.activacion",
        "kpi_kg_config_id.kpi_tabla.line_ids.cobranza",
        "kpi_kg_config_id.kpi_tabla.line_ids.cobranza_dos",
    )
    def _compute_activaciones(self):
        for rec in self:
            line_ids = rec.kpi_kg_config_id \
                .kpi_tabla.line_ids \
                .filtered(lambda x: x.numero == rec.category_active)

            rec.kpi_percent_pp = sum(line_ids.mapped('precio_promedio'))
            rec.kpi_percent_ac = sum(line_ids.mapped('activacion'))
            rec.kpi_percent_cc = sum(line_ids.mapped('cobranza'))
            rec.kpi_percent_cc_dos = sum(line_ids.mapped('cobranza_dos'))

    @api.depends('progress','goal')
    def _compute_logro(self):
        for rec in self:
            rec.actual_percent = 0

            if rec.goal != 0:
                rec.actual_percent = (rec.progress / rec.goal) * 100

    @api.depends(
        "bonification",
        "kpi_kg_config_id.kpi_tabla.precio_promedio_max",
        "kpi_percent_pp",
        "goal_average_price",
        "average_price",
    )
    def _compute_logro_average_price(self):
        for rec in self:
            rec.kpi_amount_pp = monto_kpi = (rec.bonification * rec.kpi_percent_pp) / 100
            rec.logro_average_price = percent_pp = 0

            if rec.goal_average_price != 0:
                rec.logro_average_price = percent_pp = (rec.average_price / rec.goal_average_price) * 100

            tope = (monto_kpi * rec.kpi_kg_config_id.kpi_tabla.precio_promedio_max) / 100

            monto_logrado = monto_kpi * (percent_pp / 100)
            rec.kpi_bono_pp = monto_logrado

            if monto_logrado > tope: 
                rec.kpi_bono_pp = tope

    @api.depends(
        "kpi_kg_config_id.start_date",
        "kpi_kg_config_id.end_date",
        "customers_to_active",
        "salesperson_id.user_id.partner_id.invoice_ids.partner_id",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "salesperson_id.user_id.partner_id.invoice_ids.move_type",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_date",
        "bonification",
        "kpi_percent_ac",
        "kpi_kg_config_id.kpi_tabla.activacion_max",
        "crm_team_id.user_id",
        "crm_team_id.member_ids",
        "salesperson_id.branch_id",
        "salesperson_id.branch_id.crm_team_ids.user_id",
        "salesperson_id.branch_id.crm_team_ids.member_ids",
        "rank",
        "parent_id",
    )
    def _compute_activacion(self):
        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range

            domain = [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", dates["start"]),
                ("invoice_date", "<=", dates["end"]),
            ]
            if rec.rank !='gerente_nacional':
                domain += rec.get_invoice_domain_by_rank()

            move_ids = self.env["account.move"].sudo().search(domain)

            rec.kpi_amount_ac = monto_kpi = (rec.bonification * rec.kpi_percent_ac) / 100
            rec.customer_active = cantidad = len(move_ids.mapped('partner_id'))
            rec.logro_ac = percent_ac =  (cantidad / (rec.customers_to_active or 1)) * 100

            tope = (monto_kpi * rec.kpi_kg_config_id.kpi_tabla.activacion_max) / 100
            monto_logrado =  monto_kpi * (percent_ac / 100)
            rec.kpi_bono_ac = monto_logrado

            if monto_logrado > tope: 
                rec.kpi_bono_ac = tope
           
    @api.depends(
        "rank",
        "kpi_kg_config_id.start_date",
        'salesperson_id.user_id.partner_id.invoice_ids',
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.date",
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.account_id.user_type_id.type",
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.balance",
        "crm_team_id.user_id",
        "crm_team_id.member_ids",
        "salesperson_id.branch_id",
        "salesperson_id.branch_id.crm_team_ids.user_id",
        "salesperson_id.branch_id.crm_team_ids.member_ids",
        "parent_id",
    )
    def _compute_xcobrar_pasado(self):
        for rec in self:
            domain = [
                ("state", "=", "posted"),
                ("date", "<", rec.kpi_kg_config_id.start_date),
            ]
            if rec.rank !='gerente_nacional':
                domain += rec.get_invoice_domain_by_rank()
            
            balance = self.env["account.move"].sudo() \
                .search(domain) \
                .mapped("line_ids") \
                .filtered(lambda x: x.account_id.user_type_id.type == 'receivable') \
                .mapped("balance")

            rec.xcobrar_pasado = sum(balance)

    @api.depends(
        "kpi_kg_config_id.start_date",
        "kpi_kg_config_id.end_date",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.date",
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.account_id.user_type_id.type",
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.credit",
        "crm_team_id.user_id",
        "crm_team_id.member_ids",
        "salesperson_id.branch_id",
        "salesperson_id.branch_id.crm_team_ids.user_id",
        "salesperson_id.branch_id.crm_team_ids.member_ids",
        "rank",
        "parent_id",
    )
    def _compute_xcobrar_mes(self):
        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range

            domain = [
                ("state", "=", "posted"),
                ("date", ">=", dates["start"]),
                ("date", "<=", dates["end"]),
            ]
            if rec.rank !='gerente_nacional':
                domain += rec.get_invoice_domain_by_rank()

            credits = self.env["account.move"].sudo() \
                .search(domain) \
                .mapped("line_ids") \
                .filtered(lambda x: x.account_id.user_type_id.type =='receivable') \
                .mapped("credit")

            rec.xcobrar_mes = sum(credits)

    @api.depends(
        'goal',
        'goal_average_price',
        'xcobrar_pasado',
        'kpi_percent_cc',
        'xcobrar_mes',
        "bonification",
    )
    def _compute_meta_cobranza(self):
        for rec in self:
            rec.meta_cobranza = meta = ((rec.goal * rec.goal_average_price) / 2 ) + rec.xcobrar_pasado
            rec.logro_cobranza = percent_cc = 0

            if meta !=0:
                rec.logro_cobranza = percent_cc = (rec.xcobrar_mes / meta) * 100

            rec.kpi_amount_cc = monto_kpi = (rec.bonification * rec.kpi_percent_cc) / 100

            rec.kpi_bono_cc = monto_kpi * (percent_cc / 100)

    # Cobranza Dos
    @api.depends(
        "kpi_kg_config_id.start_date",
        "kpi_kg_config_id.end_date",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
        "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
        "salesperson_id.user_id.partner_id.invoice_ids.state",
        "salesperson_id.user_id.partner_id.invoice_ids.date",
        "salesperson_id.user_id.partner_id.invoice_ids.move_type",
        "salesperson_id.user_id.partner_id.invoice_ids.payment_state",
        "salesperson_id.user_id.partner_id.invoice_ids.amount_total",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_date_due",
        "salesperson_id.user_id.partner_id.invoice_ids.amount_total",
        "kpi_kg_config_id.kpi_tabla.variante_cobranza_dos",
        "bonification",
        'kpi_percent_cc_dos',
        "crm_team_id.user_id",
        "crm_team_id.member_ids",
        "salesperson_id.branch_id",
        "salesperson_id.branch_id.crm_team_ids.user_id",
        "salesperson_id.branch_id.crm_team_ids.member_ids",
        "rank",
        "parent_id",
    )
    def _compute_meta_cobranza_dos(self):
        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range

            domain = [
                ("state", "=", "posted"),
                ('move_type','=','out_invoice'),
                ("date", ">=", dates["start"]),
                ("date", "<=", dates["end"]),
                ('payment_state','in', ('not_paid','partial'))
            ]
            if rec.rank !='gerente_nacional':
                domain += rec.get_invoice_domain_by_rank()

            move_ids = self.env["account.move"].sudo().search(domain)

            monto_facturas = sum(move_ids.mapped('amount_total'))

            rec.xcobrar_vencidas = rec.xcobrar_no_vencidas = no_vencido = 0 
            
            if monto_facturas != 0:
                rec.xcobrar_vencidas = (sum(move_ids.filtered(lambda x: x.invoice_date_due <= datetime.strptime(dates["end"], '%Y-%m-%d').date()).mapped('amount_total')) / monto_facturas) * 100
                rec.xcobrar_no_vencidas = no_vencido = (sum(move_ids.filtered(lambda x: x.invoice_date_due > datetime.strptime(dates["end"], '%Y-%m-%d').date()).mapped('amount_total')) / monto_facturas) * 100

            variante_cobranza_dos = rec.kpi_kg_config_id.kpi_tabla.variante_cobranza_dos

            rec.meta_cobranza_dos = variante_cobranza_dos
            rec.kpi_amount_cc_dos = monto_kpi = (rec.bonification * rec.kpi_percent_cc_dos) / 100
            rec.kpi_bono_cc_dos = rec.kpi_logro_cc_dos = 0

            if no_vencido > variante_cobranza_dos:
                result = (no_vencido - variante_cobranza_dos) * 2

                rec.kpi_bono_cc_dos = monto_kpi * (result / 100)
                rec.kpi_logro_cc_dos = result

    @api.depends(
        'kpi_bono_cc_dos',
        'kpi_bono_cc',
        'kpi_bono_ac',
        'kpi_bono_pp',
        'kpi_subcategory_ids.kpi_monto_logrado',
    )
    def _compute_total_bono(self):
        for rec in self:
            rec.total_bono = sum(rec.kpi_subcategory_ids.mapped('kpi_monto_logrado'))
            rec.total_bono += sum([rec.kpi_bono_cc_dos, rec.kpi_bono_cc, rec.kpi_bono_ac, rec.kpi_bono_pp])
    #endregion

    def computar_lineas(self):
        for rec in self:
            goal_total = 0
            categorias = rec.kpi_kg_config_id.mapped('kpi_categ_ids')
            sales_person = rec.kpi_kg_config_id.mapped('kpi_salesperson_id')
            if rec.rank == 'gerente_nacional':
                sales_person = sales_person.filtered(lambda y: y.rank == 'vendedor' )
                rec.goal = rec.kpi_kg_config_id.goal
            if rec.rank == 'gerente_sucursal':
                rec.goal = rec.kpi_branch_id.goal
                sales_person = sales_person.filtered(lambda y: y.rank == 'vendedor' and y.kpi_branch_id.id == rec.kpi_branch_id.id)
            if rec.rank == 'coordinador':
                sales_person = sales_person.filtered(lambda y: y.parent_id.salesperson_id.id == rec.salesperson_id.id)
            if len(rec.kpi_subcategory_ids) > 0:
                values = [(5, 0, 0)]
                rec.update({'kpi_subcategory_ids': values})
            for categ in categorias:
                goal = sum(sales_person \
                        .mapped('kpi_subcategory_ids') \
                        .filtered(lambda x: x.kpi_category_id.id == categ.id) \
                        .mapped('goal'))
                goal_total = goal_total + goal 
                line_dict = {
                    'kpi_category_id': categ.id ,
                    'goal': goal,
                }
                lines = [(0,0,line_dict)]
                rec.write({'kpi_subcategory_ids':lines})
            if rec.rank == 'coordinador':
                rec.goal = goal_total
    @api.depends('progress','goal')
    def _compute_progress_percent(self):
        for rec in self:
            rec.progress_percent = 0
            if rec.progress != 0 and rec.goal != 0:
                rec.progress_percent = round((rec.progress * 100) / rec.goal,2)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        if 'customer_active' not in fields:
            return super(KpiConfigSalesperson, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(KpiConfigSalesperson, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['customer_active'] = sum(quant.customer_active for quant in quants)
        return res