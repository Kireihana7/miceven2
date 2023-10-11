# -*- coding: utf-8 -*-

from itertools import groupby
import random
import ast
from odoo import models, api, fields, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create_from_quick_invoice(self, **kwargs):
        company = self.env.company

        try:
            partner_id = self.create({
                "country_id": company.country_id.id,
                "state_id": company.state_id.id,
                "residence_type": "R",
                **kwargs,
            })

            return {
                "partner_id": partner_id.id
            }
        except Exception as e:
            return {
                "error": e,
            }

class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_id = fields.Many2one("account.move", "Factura", tracking=True)

class AccountInvoice(models.Model):
    _inherit = "account.move"

    picking_ids = fields.One2many("stock.picking", "invoice_id", "Transferencias")

    @api.model
    def get_payments(self, partner_id):
        lines = self.env["account.move.line"].sudo().search([
            ('account_id.user_type_id.type', 'in', ('receivable', 'payable')),
            ('move_id.state', '=', 'posted'),
            ('partner_id', '=', partner_id),
            ('reconciled', '=', False),
            '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ('balance', '<', 0.0),
        ])

        lines = lines.mapped(lambda line: {
            'journal_name': line.ref or line.move_id.name,
            'amount': line.amount_residual_currency,
            'currency': line.currency_id.symbol,
            'id': line.id,
            'move_id': line.move_id.id,
            'position': line.currency_id.position,
            'digits': [69, line.currency_id.decimal_places],
            'payment_date': fields.Date.to_string(line.date),
        })

        return lines

    @api.model
    def compute_currency(self, currency_id, order_untaxes, order_total, order_taxes, payment_date):
        total = taxes = untaxes = 0
        company_currency = self.env.user.company_id.currency_id
        currency_id = self.env['res.currency'].browse(currency_id) or company_currency

        if company_currency == currency_id:
            untaxes = order_untaxes
            total = order_total
            taxes = order_taxes
        else:
            company_currency = company_currency.with_context(date=payment_date)

            untaxes += company_currency.compute(order_untaxes, currency_id)
            total += company_currency.compute(order_total, currency_id)
            taxes += company_currency.compute(order_taxes, currency_id)

        return {
            "order_untaxes": abs(untaxes),
            "order_total": abs(total),
            "order_taxes": abs(taxes),
        }

    @api.model
    def get_invoice_journals(self):
        journals = []
        account_journal = self.env['account.journal']
        settings_record = self.env['ir.config_parameter'].search_read([('key', '=', 'quick_invoice_journal_ids')], ['value'])
        if settings_record and ast.literal_eval(settings_record[0].get('value')):
            for each in ast.literal_eval(settings_record[0].get('value')):
                journal = account_journal.search_read([('id', '=', each)], ['display_name', 'code', 'type', 'company_id'])
                if journal:
                    journals.append(journal[0])
        return journals

    @api.model
    def check_user_rights(self):
        return {
            "multi_company": self.user_has_groups("base.group_multi_company"),
            "multi_currency": self.user_has_groups("base.group_multi_currency"),
        }

    @api.model
    def get_product_tax_amount(self, price_unit, quantity, product, company_id, partner,taxes=None):
        product_rec = None
        amount = 0.0
        if product:
            product_rec = self.env['product.product'].browse(product)
        if partner:
            partner = self.env['res.partner'].browse(partner.get('id'))
        if taxes is None and product_rec:
            taxes = product_rec.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id)
            vals = taxes.compute_all(price_unit=price_unit, currency=None, quantity=quantity, product=product, partner=partner)
            amount = sum(t.get('amount', 0.0) for t in vals.get('taxes', []))
            
        return amount

    @api.model
    def load_currency(self):
        return self.env.company.currency_id.read()

    def action_create_line_picking(self):
        warehouse_id = self.env["ir.config_parameter"] \
            .sudo() \
            .get_param("aspl_quick_invoice.quick_invoice_warehouse_id")

        if not warehouse_id:
            warehouse_id = self.env.user._get_default_warehouse_id()

        picking_type = warehouse_id.out_type_id
        location_dest_id = None

        if picking_type.default_location_dest_id:
            location_dest_id = picking_type.default_location_dest_id.id
        elif self.partner_id:
            location_dest_id = self.partner_id.property_stock_customer.id
        else:
            location_dest_id, _ = self.env['stock.warehouse']._get_partner_locations()

        picking_id = self.env["stock.picking"].sudo().create({
            "origin": self.name,
            "date_deadline": fields.Date.context_today(self),
            "location_id": warehouse_id.lot_stock_id.id,
            "location_dest_id": location_dest_id,
            "picking_type_id": picking_type.id,
            "partner_id": self.partner_id.id,
            "invoice_id": self.id,
        })

        move_ids = self.env["stock.move"]

        for line in self.invoice_line_ids:
            product = line.product_id

            move_ids += self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'picking_id': picking_id.id,
                'product_uom_qty': line.quantity,
                'location_id': warehouse_id.lot_stock_id.id,
                'location_dest_id': location_dest_id,
                'price_unit': line.price_unit,
                'warehouse_id': warehouse_id.id,
                'route_ids': [(6, 0, warehouse_id.route_ids.ids)],
            })

        move_ids._action_confirm()
        move_ids._action_assign()

        for product_id, lines in groupby(picking_id.move_line_ids + picking_id.move_line_ids_without_package, key=lambda l: l.product_id.id):
            line_ids = self.env["stock.move.line"].browse([line.id for line in lines])

            line_ids.write({
                "qty_done": self
                    .invoice_line_ids
                    .filtered(lambda l: l.product_id.id == product_id)
                    .quantity,
            })

        if picking_id.state != 'cancel':
            picking_id.with_context(cancel_backorder=True)._action_done()

    @api.model
    def create_invoice(self, lines, customer, payment_lines, due_amount, credits=[]):
        company_id = self.env.company

        if not all([lines, customer]):
            return {
                "error": "No hay nada que facturar"
            }

        try:
            taxes = self.env['account.tax']
            invoice_line_ids = []

            for line in lines:
                product_id = self.env['product.product'].browse(line['product_id'][0])

                name = product_id.partner_ref

                if product_id.description_purchase:
                    name += '\n' + product_id.description_purchase
                elif product_id.description_purchase and product_id.description_sale:
                    name += '\n' + product_id.description_sale

                taxes = taxes.filtered(lambda r: r.company_id == company_id)

                invoice_line_ids.append((0, 0, {
                    'account_id': product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id,
                    'name': name,
                    'product_uom_id': product_id.uom_id.id,
                    'quantity': line['quantity'],
                    'price_unit': line['price'],
                    'product_id': product_id.id,
                    'discount': line['discount'],
                    'tax_ids': [(6, 0, taxes.ids)],
                }))

            invoice_id = self.env['account.move'].create({
                'partner_id': customer.get('id'),
                'company_id': company_id.id,
                'nro_control': random.randint(1, 100),
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_line_ids,
                'invoice_date_due': fields.Datetime.today(),
                'invoice_date': fields.Datetime.today(),
            })
            
            invoice_id._onchange_partner_id()

            if due_amount == invoice_id.amount_total:
                invoice_id.state = 'draft'
            elif due_amount < invoice_id.amount_total or due_amount == 0:
                invoice_id.post()
                invoice_id.action_create_line_picking()
                invoice_id.action_register_payment()

                for payment_line in payment_lines:
                    payment_id = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice_id.id).create({
                        'amount': payment_line.get('amount'),
                        'journal_id': payment_line.get('journal_id'),
                        'payment_date': fields.Date.today(),
                        'communication': invoice_id.display_name
                    })

                    payment_id.action_create_payments()

                for credit in credits:
                    invoice_id.js_assign_outstanding_line(credit)

            return {
                'id': invoice_id.id, 
                'name': invoice_id.name,
                'partner_id': invoice_id.partner_id.name,
                'amount_total': invoice_id.amount_total
            }

        except Exception as e:
            return {
                'error':e
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
