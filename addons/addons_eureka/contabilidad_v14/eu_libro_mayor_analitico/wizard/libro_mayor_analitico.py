# -*- coding: utf-8 -*-

from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountAccount(models.Model):
    _inherit = "account.account"

    def get_lines_by_date(self, from_date, to_date):
        return self.env["account.move.line"].search([
            ("date",">=", from_date),
            ("date","<=", to_date),
            ("account_id","in",self.ids),
            ("company_id","=",self.company_id.id),
            ('move_id.state', '=',"posted"),
        ])

    def balance_by_date(self, from_date, to_date, currency_id=False):
        self.ensure_one()

        move_line_ids = self.get_lines_by_date(from_date, to_date)

        if not move_line_ids: 
            return None

        balance = credit = debit = 0

        for line in move_line_ids:
            if line.currency_id == currency_id:
                balance += line.balance
                credit += line.credit
                debit += line.debit
            else:
                balance += line.balance_usd
                credit += line.credit_usd
                debit += line.debit_usd

        return {
            "balance": balance,
            "credit": credit,
            "debit": debit,
        }

class LibroMayorAnalitico(models.TransientModel):
    _name = 'libro.mayor.analitico'
    _description = "Libro mayor analítico"

    from_date = fields.Date("Desde")
    to_date = fields.Date("Hasta")
    report_type = fields.Selection([
        ("resumido","Resumido"),
        ("detallado","Detallado"),
    ], string="Tipo de reporte", default="resumido", tracking=True)
    account_ids = fields.Many2many(
        "account.account", 
        "account_libro_mayor_rel",
        "libro_mayor_id",
        "account_id",
        "Cuentas",
    )
    all_accounts = fields.Boolean("Todas las cuentas")
    currency_id = fields.Many2one("res.currency", "Moneda", default=lambda self: self.env.company.currency_id)

    @api.onchange("all_accounts")
    def _onchange_all_accounts(self):
        self.update({"account_ids": None})

    def report_detallado(self, account_ids):
        return self.env \
            .ref("eu_libro_mayor_analitico.action_report_libro_mayor_analitico_detallado") \
            .report_action([], data={
                "from_date": self.from_date, 
                "to_date": self.to_date,
                "account_ids": account_ids,
                "currency_id": self.currency_id.id,
            })

    def report_resumido(self, account_ids):
        date_range = rrule(freq=MONTHLY, dtstart=self.from_date.replace(day=1), until=self.to_date.replace(day=1))
        date_range = [[item, item + relativedelta(day=31)] for item in date_range]
        date_range[0][0], date_range[-1][-1] = self.from_date, self.to_date

        return self.env \
            .ref("eu_libro_mayor_analitico.action_report_libro_mayor_analitico_resumido") \
            .report_action([], data={
                "from_date": self.from_date, 
                "to_date": self.to_date,
                "account_ids": account_ids,
                "date_range": date_range,
                "currency_id": self.currency_id.id,
            })

    def action_view_report(self):
        ids = self.account_ids if not self.all_accounts else self.env["account.account"].search([])
        ids = ids.filtered(lambda a: a.balance_by_date(self.from_date, self.to_date)).ids

        if not ids:
            raise UserError("No se encontraron cuentas")

        return getattr(self, "report_" + self.report_type)(ids)
