# -*- coding: utf-8 -*-

import numpy as np
from datetime import date,datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

sql_tuple = lambda t: "({})".format(",".join(map(str, t)) or "'0'")
datestr = lambda s: f"'{s}'" if s else "NULL"

COMPUTE_DEPENDS = [
    "rank",
    "crm_team_id.user_id",
    "crm_team_id.member_ids",
    "kpi_kg_config_id.end_date",
    "kpi_kg_config_id.start_date",
    "parent_id",

    #Me
    "salesperson_id.user_id",
    "salesperson_id.branch_id",
    "salesperson_id.branch_id.crm_team_ids.user_id",
    "salesperson_id.branch_id.crm_team_ids.member_ids",
    "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
    "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
    "salesperson_id.user_id.partner_id.invoice_ids.move_type",
    "salesperson_id.user_id.partner_id.invoice_ids.parent_id.invoice_date",
    "salesperson_id.user_id.partner_id.invoice_ids.date",
    "salesperson_id.user_id.partner_id.invoice_ids.state",
    "salesperson_id.user_id.partner_id.invoice_ids.invoice_date",
    "salesperson_id.user_id.partner_id.invoice_ids.payment_state",
    "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.quantity",
    "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.product_id.weight",
]

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
    category_active = fields.Integer(
        "Categorías Activadas",
        compute="_compute_category_active",
        store=True,
    )
    goal = fields.Float("Meta", tracking=True,digits=(10,2))
    # Precio Promedio
    goal_average_price = fields.Monetary("Meta P.P", tracking=True)
    average_price = fields.Monetary(
        "Precio promedio",
        compute="_compute_progress", 
        tracking=True,
        store=True,
    )
    logro_average_price = fields.Float(
        "Logro P.P %",
        compute="_compute_logro_average_price",
        tracking=True,
        store=True,
    )
    kpi_percent_pp = fields.Float(
        "KPI P.P %",
        compute="_compute_activaciones",
        tracking=True,
        store=True,
    )
    kpi_amount_pp = fields.Float(
        "Valor P.P",
        compute="_compute_logro_average_price",
        tracking=True,
        store=True,
    )
    kpi_bono_pp = fields.Float(
        "Bono P.P",
        compute="_compute_logro_average_price",
        tracking=True,
        store=True,
    )

    # Activación
    customers_to_active = fields.Integer("Clientes para activación", tracking=True)
    is_active = fields.Boolean(
        "Activo", 
        compute="_compute_progress", 
        tracking=True,
        store=True,
    )
    customer_active = fields.Integer(
        'Clientes Activados',
        compute="_compute_activacion",
        tracking=True,
        store=True,
    )
    logro_ac = fields.Float(
        "Logro Activación %",
        compute="_compute_activacion",
        tracking=True,
        store=True,
    )
    kpi_percent_ac = fields.Float(
        "KPI Activación %",
        compute="_compute_activaciones",
        tracking=True,
        store=True
    )
    kpi_amount_ac = fields.Float(
        "Valor Activación",
        compute="_compute_activacion",
        tracking=True,
        store=True,
    )
    kpi_bono_ac = fields.Float(
        "Bono Activación",
        compute="_compute_activacion",
        tracking=True,
        store=True,
    )
    
    # Volumen
    actual_percent = fields.Float(
        string="Logro Volumen %",
        compute="_compute_logro",
        tracking=True,
        store=True,
    )
    
    # Cobranza
    xcobrar_pasado = fields.Float(
        string='CxC Mes Pasado',
        compute="_compute_xcobrar_pasado",
        tracking=True,
        store=True,
    )
    xcobrar_mes = fields.Float(
        string='Cobranza',
        compute="_compute_xcobrar_mes",
        tracking=True,
        store=True,
    )
    logro_cobranza = fields.Float(
        string="Logro Cobranza %",
        compute="_compute_meta_cobranza",
        tracking=True,
        store=True
    )
    kpi_percent_cc = fields.Float(
        string="KPI Cobranza %",
        compute="_compute_activaciones",
        tracking=True,
        store=True
    )
    meta_cobranza = fields.Float(
        string="Meta Cobranza",
        compute="_compute_meta_cobranza",
        tracking=True,
        store=True
    )
    kpi_amount_cc = fields.Float(
        string="Valor Cobranza",
        compute="_compute_meta_cobranza",
        tracking=True,
        store=True
    )
    kpi_bono_cc = fields.Float(
        string="Bono Cobranza",
        compute="_compute_meta_cobranza",
        tracking=True,
        store=True
    )

    #Cobranza 2
    xcobrar_vencidas = fields.Float(
        string="Cxc Vencidas",
        compute="_compute_meta_cobranza_dos",
        tracking=True,
        store=True,
    )
    xcobrar_no_vencidas = fields.Float(
        string="Cxc No Vencidas",
        compute="_compute_meta_cobranza_dos",
        tracking=True,
        store=True,
    )
    kpi_logro_cc_dos = fields.Float(
        string="Logro Cobranza Dos %",
        compute="_compute_meta_cobranza_dos",
        tracking=True,
        store=True,
    )
    kpi_percent_cc_dos = fields.Float(
        string="KPI Cobranza Dos %",
        compute="_compute_activaciones",
        tracking=True,
        store=True,
    )
    meta_cobranza_dos = fields.Float(
        string="Meta Cobranza Dos",
        compute="_compute_meta_cobranza_dos",
        tracking=True,
        store=True,
    )
    kpi_amount_cc_dos = fields.Float(
        string="Valor Cobranza Dos",
        compute="_compute_meta_cobranza_dos",
        tracking=True,
        store=True,
    )
    kpi_bono_cc_dos = fields.Float(
        string="Bono Cobranza Dos",
        compute="_compute_meta_cobranza_dos",
        tracking=True,
        store=True,
    )

    # Total Bono
    total_bono = fields.Float(
        "Total Bono",
        compute="_compute_total_bono",
        tracking=True, 
        store=True
    )
    devoluciones = fields.Float(
        "Devoluciones", 
        compute="_compute_devoluciones",
        tracking=True,
        store=True,
    )
    venta_mes = fields.Float(
        "Venta del Mes", 
        compute="_compute_venta_mes",
        tracking=True,
        store=True
    )
    bonification = fields.Float(
        "Bonificación", 
        compute="_compute_bonification",
        tracking=True, 
        store=True
    )

    def get_invoice_user_ids(self):
        mapped = lambda t: t.user_id + t.member_ids
        invoice_user_ids = []

        if not self.salesperson_id:
            return invoice_user_ids
        
        if self.rank == "vendedor":
            invoice_user_ids = self.salesperson_id.user_id.ids
        elif self.rank == "coordinador":
            invoice_user_ids = self.with_context(active_test=False) \
                .crm_team_id \
                .mapped(mapped) \
                .ids
        elif self.rank == "gerente_sucursal":
            invoice_user_ids = self.env["crm.team"].with_context(active_test=False) \
                .search([("branch_id", "=", self.salesperson_id.branch_id.id)]) \
                .mapped(mapped) \
                .ids
            
        return invoice_user_ids

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

    @api.depends(*COMPUTE_DEPENDS)    
    def _compute_devoluciones(self):
        for rec in self:
            branch = rec.salesperson_id.branch_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            config = rec.kpi_kg_config_id
            dates: dict[str, date] = config.date_range

            query = f"""
SELECT SUM(weight) FROM (SELECT SUM(pp.weight * aml.quantity) AS weight
FROM account_move_line aml
RIGHT JOIN account_move am ON aml.move_id = am.id 
RIGHT JOIN account_move parent on am.parent_id = parent.id
RIGHT JOIN product_product pp ON aml.product_id = pp.id
WHERE 
    am.move_type = 'out_refund' AND
    am.state = 'posted' AND
	parent.invoice_date <= {datestr(dates["start"])} AND
    am.invoice_date >= {datestr(dates["start"])} AND
    am.invoice_date <= {datestr(dates["end"])}
"""

            if user_ids:
                query += f"AND am.invoice_user_id in {sql_tuple(user_ids)}"

            if rec.rank !='gerente_nacional' and branch:
                query += f"AND am.branch_id = {branch}"

            query += "GROUP BY am.move_type ORDER BY am.move_type) l"

            self.env.cr.execute(query)
    
            result = self.env.cr.dictfetchone()
            rec.devoluciones = result.get("sum", 0) if result else 0

    @api.depends("devoluciones", "progress")            
    def _compute_venta_mes(self):
        for rec in self:
            rec.venta_mes = rec.progress + rec.devoluciones
            
    @api.depends(
        "devoluciones",
        "goal_average_price",
        "customers_to_active",
        "salesperson_id.user_id.partner_id.invoice_ids.partner_id",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.price_subtotal",
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_line_ids.weight_total",
        *COMPUTE_DEPENDS,
    )
    def _compute_progress(self):
        select = """
am.partner_id as partner,
aml.move_type as type,
ROUND(pp.weight * aml.quantity, 4) AS quantity,
ROUND(SUM(aml.price_subtotal), 4) AS subtotal,
ROUND(SUM(aml.weight_total)::numeric, 4) AS weight
        """

        groupby = "GROUP BY aml.id, partner, type, pp.weight, aml.quantity"

        for rec in self:
            branch = rec.salesperson_id.branch_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            config = rec.kpi_kg_config_id
            dates: dict[str, date] = config.date_range

            out_query = f"""
SELECT {select}
FROM account_move_line aml
LEFT JOIN account_move am ON aml.move_id = am.id
LEFT JOIN product_product pp ON aml.product_id = pp.id
WHERE
	am.state = 'posted' AND
    aml.product_id IS NOT NULL AND
    aml.move_type  = 'out_invoice' AND
    am.invoice_date >= {datestr(dates["start"])} AND
    am.invoice_date <= {datestr(dates["end"])}
"""

            refund_query = f"""
SELECT {select}
FROM account_move_line aml
LEFT JOIN account_move am ON aml.move_id = am.id
LEFT JOIN account_move parent ON am.parent_id = parent.id
LEFT JOIN product_product pp ON aml.product_id = pp.id
WHERE
	am.state = 'posted' AND
    aml.product_id IS NOT NULL AND
    aml.move_type  = 'out_refund' AND
    am.invoice_date >= {datestr(dates["start"])} AND
    am.invoice_date <= {datestr(dates["end"])} AND
    parent.invoice_date >= {datestr(dates["start"])} AND
    parent.invoice_date <= {datestr(dates["end"])}
"""

            if user_ids:
                user_and = f"AND am.invoice_user_id in {sql_tuple(user_ids)}"
                out_query += user_and
                refund_query += user_and

            if rec.rank !='gerente_nacional' and branch:
                branch_cond = f"AND am.branch_id = {branch}"

                out_query += branch_cond
                refund_query += branch_cond

            out_query += groupby
            refund_query += groupby

            self.env.cr.execute(out_query)

            out_move_ids = self.env.cr.dictfetchall()

            self.env.cr.execute(refund_query)

            refund_move_ids = self.env.cr.dictfetchall()

            rec.progress = sum(m["quantity"] or 0 for m in out_move_ids) -\
                sum(m["quantity"] or 0 for m in refund_move_ids) -\
                rec.devoluciones

            rec.is_active = len(set(m["partner"] for m in (refund_move_ids + out_move_ids))) >= rec.customers_to_active
            rec.average_price = sum(m['subtotal'] for m in out_move_ids) / (sum(m['weight'] for m in out_move_ids) or 1)

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
        "customers_to_active",
        "bonification",
        "kpi_percent_ac",
        "kpi_kg_config_id.kpi_tabla.activacion_max",
        "salesperson_id.user_id.partner_id.invoice_ids.partner_shipping_id",
        *COMPUTE_DEPENDS
    )
    def _compute_activacion(self):
        for rec in self:
            branch = rec.salesperson_id.branch_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            config = rec.kpi_kg_config_id
            dates: dict[str, date] = config.date_range

            query = f"""
SELECT COUNT(*) FROM (SELECT 
    partner_id AS partner,
    partner_shipping_id AS shipping
FROM account_move
WHERE
    state = 'posted' AND
    move_type = 'out_invoice' AND
    invoice_date >= {datestr(dates["start"])} AND
    invoice_date <= {datestr(dates["end"])}
"""

            if user_ids:
                query += f"AND invoice_user_id in {sql_tuple(user_ids)}"

            if rec.rank !='gerente_nacional' and branch:
                query += f"AND branch_id = {branch}"

            query += "GROUP BY partner, shipping) l"


            rec.kpi_amount_ac = monto_kpi = (rec.bonification * rec.kpi_percent_ac) / 100

            self.env.cr.execute(query)
            result = self.env.cr.dictfetchone()

            rec.customer_active = cantidad = result.get("count", 0) if result else 0

            rec.logro_ac = percent_ac =  (cantidad / (rec.customers_to_active or 1)) * 100

            tope = (monto_kpi * config.kpi_tabla.activacion_max) / 100
            monto_logrado =  monto_kpi * (percent_ac / 100)
            rec.kpi_bono_ac = monto_logrado

            if monto_logrado > tope: 
                rec.kpi_bono_ac = tope
           
    @api.depends(
        "kpi_kg_config_id.start_date",
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.balance",
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.account_id.user_type_id.type",
        *COMPUTE_DEPENDS,
    )
    def _compute_xcobrar_pasado(self):
        for rec in self:
            branch = rec.salesperson_id.branch_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            
            query = f"""
SELECT SUM(aml.balance) AS balance
FROM account_move_line aml
LEFT JOIN account_move am ON am.id = aml.move_id
LEFT JOIN account_account ac ON ac.id = aml.account_id
LEFT JOIN account_account_type act ON act.id = ac.user_type_id
WHERE
    am.state = 'posted' AND
    act.type = 'receivable' AND
    am.date < {datestr(rec.kpi_kg_config_id.start_date)}
"""

            if user_ids:
                query += f"AND am.invoice_user_id in {sql_tuple(user_ids)}"

            if rec.rank !='gerente_nacional' and branch:
                query += f"AND am.branch_id = {branch}"

            self.env.cr.execute(query)

            result = self.env.cr.dictfetchone()
            rec.xcobrar_pasado = result.get("sum", 0) if result else 0

    @api.depends(
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.credit",
        *COMPUTE_DEPENDS,
    )
    def _compute_xcobrar_mes(self):
        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range
            salesperson = rec.salesperson_id
            branch = salesperson.branch_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            
            query = f"""
SELECT SUM(aml.credit) AS credit
FROM account_move_line aml
LEFT JOIN account_move am ON am.id = aml.move_id
LEFT JOIN account_account ac ON ac.id = aml.account_id
LEFT JOIN account_account_type act ON act.id = ac.user_type_id
WHERE
    aml.parent_state = 'posted' AND
    act.type = 'receivable' AND
    am.date >= {datestr(dates["start"])} AND
    am.date <= {datestr(dates["end"])}
"""
            if user_ids:
                query += f"AND am.invoice_user_id in {sql_tuple(user_ids)}"

            if rec.rank !='gerente_nacional' and branch:
                query += f"AND am.branch_id = {branch}"

            self.env.cr.execute(query)

            result = self.env.cr.dictfetchone()
            rec.xcobrar_mes = result.get("credit", 0) if result else 0

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
        "kpi_kg_config_id.kpi_tabla.variante_cobranza_dos",
        "bonification",
        'kpi_percent_cc_dos',
        "salesperson_id.user_id.partner_id.invoice_ids.invoice_date_due",
        "salesperson_id.user_id.partner_id.invoice_ids.amount_total",
        *COMPUTE_DEPENDS
    )
    def _compute_meta_cobranza_dos(self):
        parse = lambda d: datetime.strptime(d, '%Y-%m-%d').date() if type(d) == str \
            else d if type(d) == date \
            else d.date()

        for rec in self:
            dates: dict[str, date] = rec.kpi_kg_config_id.date_range
            salesperson = rec.salesperson_id
            branch = salesperson.branch_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            
            query = f"""
SELECT 
    invoice_date_due,
    SUM(amount_total) as amount_total
FROM account_move
WHERE 
    move_type = 'out_invoice' AND
    payment_state IN ('not_paid','partial') AND
    state = 'posted' AND
    date >= {datestr(dates['start'])} AND
    date <= {datestr(dates['end'])}
"""

            if user_ids:
                query += f"AND invoice_user_id in {sql_tuple(user_ids)}"

            if rec.rank !='gerente_nacional' and branch:
                query += f"AND branch_id = {branch}"

            query += "GROUP BY invoice_date_due"

            self.env.cr.execute(query)

            move_ids = self.env.cr.dictfetchall()

            monto_facturas = sum(r['amount_total'] or 0 for r in move_ids)

            rec.xcobrar_vencidas = rec.xcobrar_no_vencidas = no_vencido = 0 
            
            if monto_facturas != 0:
                rec.xcobrar_vencidas = sum(r['amount_total'] or 0 for r in move_ids if parse(r["invoice_date_due"]) <= parse(dates["end"])) / monto_facturas * 100
                rec.xcobrar_no_vencidas = no_vencido = sum(r['amount_total'] or 0 for r in move_ids if parse(r["invoice_date_due"]) > parse(dates["end"])) / monto_facturas * 100

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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        if 'customer_active' not in fields:
            return res
        
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['customer_active'] = sum(quant.customer_active for quant in quants)

        return res