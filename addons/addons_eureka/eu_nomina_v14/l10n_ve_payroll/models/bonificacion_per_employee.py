# -*- coding: utf-8 -*-


from odoo import models, fields,api

class BonificationPerEmployee(models.Model):
    _name = 'bonification.per.employee'

    date_efective=fields.Date("Fecha efectiva")
    employee_id=fields.Many2one("hr.employee", "Empleado")
    concept=fields.Char("Concepto")
    code=fields.Char("Código")
    company_id = fields.Many2one('res.company',string="Compañía", default=lambda self: self.env.company.id,tracking=True,invisible=True)
    currency_id = fields.Many2one("res.currency", string="Moneda",default=lambda self: self.company_id.currency_id)
    cantidad=fields.Float("Cantidad")
    monto_unitario=fields.Float("Monto Unit.")
    monto=fields.Float("Monto",compute="_compute_total",store=True)

    @api.depends("cantidad","monto_unitario")
    def _compute_total(self):
        for rec in self:
            rec.monto=rec.cantidad*rec.monto_unitario





class ComisionesPerEmployee(models.Model):
    _name = 'comisiones.per.employee'

    date_efective=fields.Date("Fecha efectiva")
    employee_id=fields.Many2one("hr.employee", "Empleado")
    concept=fields.Char("Concepto")
    code=fields.Char("Código")
    company_id = fields.Many2one('res.company',string="Compañía", default=lambda self: self.env.company.id,tracking=True,invisible=True)
    currency_id = fields.Many2one("res.currency", string="Moneda",default=lambda self: self.company_id.currency_id)
    cantidad=fields.Float("Cantidad")
    monto_unitario=fields.Float("Monto Unit.")
    monto=fields.Float("Monto",compute="_compute_total",store=True)

    @api.depends("cantidad","monto_unitario")
    def _compute_total(self):
        for rec in self:
            rec.monto=rec.cantidad*rec.monto_unitario


