# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from datetime import date


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'


    @api.constrains('state')
    def get_actual_posting(self):
        for record in self:
            if record.state in [('done'),('cancel')]:
                record._direct_cost_postings()
        return True

    # production direct cost posting
    def _direct_cost_postings(self):
        total_working_duration = 0.0
        total_fixed_duration = 0.0
        amount_working = 0.0
        amount_fixed = 0.0
        final_date = False
        for record in self:
            desc_wo = record.production_id.name + '-' + record.workcenter_id.name + '-' + record.name
            last_time = self.env['mrp.workcenter.productivity'].search([('workorder_id', '=', record.id),('date_end', '!=', False)], order=	"date_end desc", limit=1)
            if last_time:
                final_date = last_time.date_end.date()
            else:
                final_date = date.today()
            analytic_account = record.production_id.analytic_account_id.id or record.workcenter_id.analytic_account_id.id
            for time in record.time_ids:
                if time.overall_duration:
                    total_working_duration += time.working_duration
                    total_fixed_duration += time.setup_duration + time.teardown_duration
                else:
                    total_working_duration += time.duration
            amount_working = round((total_working_duration * record.workcenter_id.costs_hour)/ 60, 2)
            amount_fixed = round((total_fixed_duration * record.workcenter_id.costs_hour_fixed)/ 60, 2)
            if amount_working:
                if record.workcenter_id.wc_type == "H":
                    account_id = record.production_id.company_id.labour_cost_account_id
                else:
                    account_id = record.production_id.company_id.machine_run_cost_account_id
                id_created_header = self.env['account.move'].create({
                    'journal_id' : record.production_id.company_id.manufacturing_journal_id.id,
                    'date': final_date,
                    'ref' : "Direct Variable Costs",
                    'company_id': record.workcenter_id.company_id.id,
                })
                id_credit_item = self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'move_id' : id_created_header.id,
                    'account_id': account_id.id,
                    'product_id': record.production_id.product_id.id,
                    'name' : desc_wo,
                    'quantity': record.qty_output_wo,
                    'product_uom_id': record.production_id.product_uom_id.id,
                    'credit': amount_working,
                    'debit': 0.0,
                    'manufacture_order_id': record.production_id.id,
                })
                id_debit_item= self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'move_id' : id_created_header.id,
                    'account_id': record.production_id.product_id.property_stock_production.valuation_in_account_id.id,
                    'analytic_account_id' : analytic_account,
                    'product_id': record.production_id.product_id.id,
                    'name' : desc_wo,
                    'quantity': record.qty_output_wo,
                    'product_uom_id': record.production_id.product_uom_id.id,
                    'credit': 0.0,
                    'debit': amount_working,
                    'manufacture_order_id': record.production_id.id,
                })
                id_created_header.post()
            if amount_fixed:
                if record.workcenter_id.wc_type == "H":
                    account_id = record.production_id.company_id.labour_fixed_cost_account_id
                else:
                    account_id = record.production_id.company_id.machine_run_fixed_cost_account_id
                id_created_header = self.env['account.move'].create({
                    'journal_id' : record.production_id.company_id.manufacturing_journal_id.id,
                    'date': final_date,
                    'ref' : "Direct Fixed Costs",
                    'company_id': record.workcenter_id.company_id.id,
                })
                id_credit_item = self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'move_id' : id_created_header.id,
                    'account_id': account_id.id,
                    'product_id': record.production_id.product_id.id,
                    'name' : desc_wo,
                    'quantity': record.qty_output_wo,
                    'product_uom_id': record.production_id.product_uom_id.id,
                    'credit': amount_fixed,
                    'debit': 0.0,
                    'manufacture_order_id': record.production_id.id,
                })
                id_debit_item= self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'move_id' : id_created_header.id,
                    'account_id': record.production_id.product_id.property_stock_production.valuation_in_account_id.id,
                    'analytic_account_id' : analytic_account,
                    'product_id': record.production_id.product_id.id,
                    'name' : desc_wo,
                    'quantity': record.qty_output_wo,
                    'product_uom_id': record.production_id.product_uom_id.id,
                    'credit': 0.0,
                    'debit': amount_fixed,
                    'manufacture_order_id': record.production_id.id,
                })
                id_created_header.post()
        return True