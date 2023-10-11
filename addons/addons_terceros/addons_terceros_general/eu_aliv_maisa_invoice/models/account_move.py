# -*- coding: utf-8 -*-

# Odoo:
from odoo import _, api, fields, models  # noqa
from odoo.tools.misc import formatLang, format_date

class MethodPayment(models.Model):
    _name = 'metodo.pago.account'
    _description ="forma de pago "
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Forma de Pago")
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company)


class AccountMove(models.Model):
    _inherit = "account.move"
    _description  = ""


    payment_method = fields.Many2one('metodo.pago.account',string="Forma de Pago")
    vehicle_id      = fields.Many2one('fleet.vehicle', string="Vehículo",compute="_compute_fleet")
    driver_id = fields.Many2one('res.partner', string="Conductor", compute="_compute_fleet")
    license_plate = fields.Char(string="Placa", compute="_compute_fleet")
    vehicle_type_property    = fields.Selection([
        ('propio', 'Propio'),
        ('tercero', 'De tercero'),
        ], string="¿Es un vehículo de Tercero?", copy=False, compute="_compute_fleet")
    notas_entregas = fields.Char(string="Codigo Notas de Entregas", compute="_compute_fleet")
    def _compute_fleet(self):
        for invoice in self:
            invoice.vehicle_id = False
            invoice.vehicle_type_property = False
            invoice.driver_id = False
            invoice.license_plate = False
            invoice.notas_entregas = False
            arre = []
            str_pic = ''
            if invoice.invoice_origin:
                if invoice.invoice_origin.find(','):

                    for x in invoice.invoice_origin.split(','):
                        arre.append(x)

                    so = self.env["sale.order"].search([("name", "=", arre[0])],limit=1)
                    if so:
                        invoice.vehicle_id = so.vehicle_id.id
                        invoice.vehicle_type_property = so.vehicle_id.vehicle_type_property
                        invoice.driver_id = so.vehicle_id.driver_id
                        invoice.license_plate = so.vehicle_id.license_plate
                        
                        for s in self.env['sale.order'].search([]):
                            if s.order_line.invoice_lines.move_id.filtered(lambda r: r.id == invoice.id):
                                for pick in s.picking_ids:
                                    if pick.sequence != False:
                                        str_pic += str(pick.sequence) + ' - '  or ''
                        invoice.notas_entregas = str_pic
                    
                    po = self.env["purchase.order"].search([("name", "=", arre[0])],limit=1)
                    if po:
                        invoice.vehicle_id = po.vehicle_id.id
                        invoice.vehicle_type_property = po.vehicle_id.vehicle_type_property
                        invoice.driver_id = po.vehicle_id.driver_id
                        invoice.license_plate = po.vehicle_id.license_plate
                        
                        for s in self.env['purchase.order'].search([]):
                            if s.order_line.invoice_lines.move_id.filtered(lambda r: r.id == invoice.id):
                                for pick in s.picking_ids:
                                    if pick.sequence != False:
                                        str_pic += str(pick.sequence) + ' - '  or ''
                        invoice.notas_entregas = str_pic
                else:
                    so = self.env["sale.order"].search([("name", "=", invoice.invoice_origin)],limit=1)
                    if so:
                        invoice.vehicle_id = so.vehicle_id.id
                        invoice.vehicle_type_property = so.vehicle_id.vehicle_type_property
                        invoice.driver_id = so.vehicle_id.driver_id
                        invoice.license_plate = so.vehicle_id.license_plate
                        str_pic = ''
                        for pick in so.picking_ids.filtered(lambda line: line.state == 'done'):
                            str_pic += pick.sequence
                        invoice.notas_entregas = str_pic
                    po = self.env["purchase.order"].search([("name", "=", invoice.invoice_origin)],limit=1)
                    if po:
                        invoice.vehicle_id = po.vehicle_id.id
                        invoice.vehicle_type_property = po.vehicle_id.vehicle_type_property
                        invoice.driver_id = po.vehicle_id.driver_id
                        invoice.license_plate = po.vehicle_id.license_plate
                        str_pic = ''
                        for pick in po.picking_ids.filtered(lambda line: line.state == 'done'):
                            str_pic += pick.sequence
                        invoice.notas_entregas = str_pic

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
    def _compute_invoice_taxes_by_group(self):
        ''' Helper to get the taxes grouped according their account.tax.group.
        This method is only used when printing the invoice.
        '''
        res = super(AccountMove, self)._compute_invoice_taxes_by_group()
        for move in self:
            lang_env = move.with_context(lang=move.partner_id.lang).env
            tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
            tax_balance_multiplicator = -1 if move.is_inbound(True) else 1
            res = {}
            # There are as many tax line as there are repartition lines
            done_taxes = set()
            for line in tax_lines:
                res.setdefault(line.tax_line_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
                res[line.tax_line_id.tax_group_id]['amount'] += tax_balance_multiplicator * (line.amount_currency if line.currency_id else line.balance)
                tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    if line.currency_id and line.company_currency_id and line.currency_id != line.company_currency_id:
                        amount = line.company_currency_id._convert(line.tax_base_amount, line.currency_id, line.company_id, line.date or fields.Date.context_today(self))
                    else:
                        amount = line.tax_base_amount
                    res[line.tax_line_id.tax_group_id]['base'] += amount
                    # The base should be added ONCE
                    done_taxes.add(tax_key_add_base)

            # At this point we only want to keep the taxes with a zero amount since they do not
            # generate a tax line.
            zero_taxes = set()
            for line in move.line_ids:
                for tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax.tax_group_id not in res or tax.tax_group_id in zero_taxes:
                        res.setdefault(tax.tax_group_id, {'base': 0.0, 'amount': 0.0})
                        res[tax.tax_group_id]['base'] += tax_balance_multiplicator * (line.amount_currency if line.currency_id else line.balance)
                        zero_taxes.add(tax.tax_group_id)

            res = sorted(res.items(), key=lambda l: l[0].sequence)
            move.amount_by_group = [(
                group.name, #0
                amounts['amount'],#1
                amounts['base'],#2
                formatLang(lang_env, amounts['amount'], currency_obj=move.currency_id),#3
                formatLang(lang_env, amounts['base'], currency_obj=move.currency_id),#4
                len(res),#5
                group.id,#6
                formatLang(lang_env, amounts['amount'] * move.manual_currency_exchange_rate),#7
                formatLang(lang_env, amounts['base'] *  move.manual_currency_exchange_rate),#8            
            ) for group, amounts in res]                



