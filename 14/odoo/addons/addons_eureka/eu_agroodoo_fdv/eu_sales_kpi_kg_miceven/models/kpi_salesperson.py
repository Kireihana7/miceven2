# -*- coding: utf-8 -*-

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
    "salesperson_id.zone_id",
    "salesperson_id.zone_id.crm_team_ids.user_id",
    "salesperson_id.zone_id.crm_team_ids.member_ids",
    "salesperson_id.user_id.partner_id.invoice_ids.invoice_user_id",
    "salesperson_id.user_id.partner_id.invoice_ids.branch_id",
    "salesperson_id.user_id.partner_id.invoice_ids.zone_id",
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
    _inherit = "kpi.config.salesperson"

    tipo_kpi = fields.Selection(string="Tipo de KPI",related="kpi_kg_config_id.tipo_kpi")

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
            domain = []
            if self.tipo_kpi == 'branch':
                domain= [("branch_id", "=", self.salesperson_id.branch_id.id)]
            else:
                domain= [("zone_id", "=", self.salesperson_id.zone_id.id)]
            invoice_user_ids = self.env["crm.team"].with_context(active_test=False) \
                .search(domain) \
                .mapped(mapped) \
                .ids
            
        return invoice_user_ids
    
    @api.depends(*COMPUTE_DEPENDS)    
    def _compute_devoluciones(self):
        for rec in self:
            branch = rec.salesperson_id.branch_id.id
            zone = rec.salesperson_id.zone_id.id
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

            if rec.rank !='gerente_nacional' and branch and rec.tipo_kpi =='branch':
                query += f"AND am.branch_id = {branch}"
            if rec.rank !='gerente_nacional' and zone and rec.tipo_kpi =='zona':
                query += f"AND am.zone_id = {zone}"

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
            zone = rec.salesperson_id.zone_id.id
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

            if rec.rank !='gerente_nacional' and branch and rec.tipo_kpi =='branch':
                branch_cond = f"AND am.branch_id = {branch}"

                out_query += branch_cond
                refund_query += branch_cond
            if rec.rank !='gerente_nacional' and zone and rec.tipo_kpi =='zona':
                branch_cond = f"AND am.zone_id = {zone}"

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
            zone = rec.salesperson_id.zone_id.id
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

            if rec.rank !='gerente_nacional' and branch and rec.tipo_kpi == 'branch':
                query += f"AND branch_id = {branch}"
            if rec.rank !='gerente_nacional' and zone and rec.tipo_kpi == 'zona':
                query += f"AND zone_id = {zone}"

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
        "salesperson_id.user_id.partner_id.invoice_ids.line_ids.account_id.account_type",
        *COMPUTE_DEPENDS,
    )
    def _compute_xcobrar_pasado(self):
        for rec in self:
            branch = rec.salesperson_id.branch_id.id
            zone = rec.salesperson_id.zone_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            
            query = f"""
SELECT SUM(aml.balance) AS balance
FROM account_move_line aml
LEFT JOIN account_move am ON am.id = aml.move_id
LEFT JOIN account_account ac ON ac.id = aml.account_id
WHERE
    am.state = 'posted' AND
    ac.account_type = 'receivable' AND
    am.date < {datestr(rec.kpi_kg_config_id.start_date)}
"""

            if user_ids:
                query += f"AND am.invoice_user_id in {sql_tuple(user_ids)}"
            if rec.rank !='gerente_nacional' and branch and rec.tipo_kpi == 'branch':
                query += f"AND am.branch_id = {branch}"
            if rec.rank !='gerente_nacional' and zone and rec.tipo_kpi == 'zona':
                query += f"AND am.zone_id = {zone}"

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
            zone = salesperson.zone_id.id
            user_ids: list[int] = rec.get_invoice_user_ids()
            
            query = f"""
SELECT SUM(aml.credit) AS credit
FROM account_move_line aml
LEFT JOIN account_move am ON am.id = aml.move_id
LEFT JOIN account_account ac ON ac.id = aml.account_id
WHERE
    aml.parent_state = 'posted' AND
    ac.account_type = 'receivable' AND
    am.date >= {datestr(dates["start"])} AND
    am.date <= {datestr(dates["end"])}
"""
            if user_ids:
                query += f"AND am.invoice_user_id in {sql_tuple(user_ids)}"

            if rec.rank !='gerente_nacional' and branch and rec.tipo_kpi == 'branch':
                query += f"AND am.branch_id = {branch}"
            if rec.rank !='gerente_nacional' and zone and rec.tipo_kpi == 'zona':
                query += f"AND am.zone_id = {zone}"
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
            zone = salesperson.zone_id.id
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
            if rec.rank !='gerente_nacional' and branch and rec.tipo_kpi == 'branch':
                query += f"AND branch_id = {branch}"
            if rec.rank !='gerente_nacional' and zone and rec.tipo_kpi == 'zona':
                query += f"AND zone_id = {zone}"

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