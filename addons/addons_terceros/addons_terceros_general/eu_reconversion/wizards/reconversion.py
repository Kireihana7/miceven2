# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ReconversionData(models.TransientModel):
    _name = 'reconversion.data'
    _description = 'Reconversion Data'

    reconversion_validate = fields.Boolean("¿Está seguro que desea realizar la Reconversión?")

    def actualizar_productos(self):
        instalado = True if self.env['ir.module.module'].search([('name','=','account'),('state','=','installed')]) else False
        if instalado:
            for product in self.env['product.template'].search([('standard_price','<=',10000),('standard_price','>',0)]):
                product.standard_price = 10000
        else: 
            raise UserError('No tiene el módulo de Facturación Instalado.')

    def reconversion(self):
        if self.reconversion_validate:
            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_move');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_move 
                SET 
                amount_untaxed = CASE WHEN (amount_untaxed > 10000 OR amount_untaxed < -10000) AND amount_untaxed != 0 THEN ROUND(amount_untaxed / 1000000,2) ELSE CASE WHEN amount_untaxed != 0 THEN 0.01 ELSE 0.0 END END,
                amount_tax = CASE WHEN (amount_tax > 10000 OR amount_tax < -10000) AND amount_tax != 0 THEN ROUND(amount_tax / 1000000,2) ELSE CASE WHEN amount_tax != 0 THEN  0.01 ELSE 0.0 END END,
                amount_total = CASE WHEN (amount_total > 10000 OR amount_total < -10000) AND amount_total != 0 THEN ROUND(amount_total / 1000000,2) ELSE CASE WHEN amount_total != 0 THEN  0.01 ELSE 0.0 END END,
                amount_residual = CASE WHEN (amount_residual > 10000 OR amount_residual < -10000) AND amount_residual != 0 THEN ROUND(amount_residual / 1000000,2) ELSE CASE WHEN amount_residual != 0 THEN  0.01 ELSE 0.0 END END,
                amount_untaxed_signed = CASE WHEN (amount_untaxed_signed > 10000 OR amount_untaxed_signed < -10000) AND amount_untaxed_signed != 0 THEN ROUND(amount_untaxed_signed / 1000000,2) ELSE CASE WHEN amount_untaxed_signed != 0 THEN  0.01 ELSE 0.0 END END,
                amount_tax_signed = CASE WHEN (amount_tax_signed > 10000 OR amount_tax_signed < -10000) AND amount_tax_signed != 0 THEN ROUND(amount_tax_signed / 1000000,2) ELSE CASE WHEN amount_tax_signed != 0 THEN  0.01 ELSE 0.0 END END,
                amount_total_signed = CASE WHEN (amount_total_signed > 10000  OR amount_total_signed < -10000) AND amount_total_signed != 0 THEN ROUND(amount_total_signed / 1000000,2) ELSE CASE WHEN amount_total_signed != 0 THEN  0.01 ELSE 0.0 END END,
                amount_residual_signed = CASE WHEN (amount_residual_signed > 10000 OR amount_residual_signed < -10000) AND amount_residual_signed != 0 THEN ROUND(amount_residual_signed / 1000000,2) ELSE CASE WHEN amount_residual_signed != 0 THEN  0.01 ELSE 0.0 END END,
                asset_remaining_value = CASE WHEN (asset_remaining_value > 10000 OR asset_remaining_value < -10000) AND asset_remaining_value != 0 THEN ROUND(asset_remaining_value / 1000000,2) ELSE CASE WHEN asset_remaining_value != 0 THEN  0.01 ELSE 0.0 END END,
                asset_depreciated_value = CASE WHEN (asset_depreciated_value > 10000 OR asset_depreciated_value < -10000) AND asset_depreciated_value != 0 THEN ROUND(asset_depreciated_value / 1000000,2) ELSE CASE WHEN asset_depreciated_value != 0 THEN  0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """
                UPDATE account_move 
                SET 
                amount_residual_signed = CASE WHEN (amount_residual_signed > 10000 OR amount_residual_signed < -10000) AND amount_residual_signed != 0 THEN ROUND(amount_residual_signed / 1000000,2) ELSE CASE WHEN amount_residual_signed != 0 THEN  0.01 ELSE 0.0 END END,
                amount_untaxed_signed = CASE WHEN (amount_untaxed_signed > 10000 OR amount_untaxed_signed < -10000) AND amount_untaxed_signed != 0 THEN ROUND(amount_untaxed_signed / 1000000,2) ELSE CASE WHEN amount_untaxed_signed != 0 THEN  0.01 ELSE 0.0 END END,
                amount_tax_signed = CASE WHEN (amount_tax_signed > 10000 OR amount_tax_signed < -10000) AND amount_tax_signed != 0 THEN ROUND(amount_tax_signed / 1000000,2) ELSE CASE WHEN amount_tax_signed != 0 THEN  0.01 ELSE 0.0 END END,
                amount_total_signed = CASE WHEN (amount_total_signed > 10000  OR amount_total_signed < -10000) AND amount_total_signed != 0 THEN ROUND(amount_total_signed / 1000000,2) ELSE CASE WHEN amount_total_signed != 0 THEN  0.01 ELSE 0.0 END END
                WHERE currency_id != 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_move_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_move_line
                SET 
                debit = CASE WHEN (debit > 10000 OR debit < -10000) AND debit != 0 THEN ROUND(debit / 1000000,2) ELSE CASE WHEN debit != 0 THEN CASE WHEN debit > 0 AND debit != 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                credit = CASE WHEN (credit > 10000 OR credit < -10000) AND credit != 0 THEN ROUND(credit / 1000000,2) ELSE CASE WHEN credit != 0 THEN CASE WHEN credit > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                balance = CASE WHEN (balance > 10000 OR balance < -10000) AND balance != 0 THEN ROUND(balance / 1000000,2) ELSE CASE WHEN balance != 0 THEN  CASE WHEN balance > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                price_unit = CASE WHEN (price_unit > 10000 OR price_unit < -10000) AND price_unit != 0 THEN ROUND(price_unit / 1000000,2) ELSE CASE WHEN price_unit != 0 THEN  CASE WHEN price_unit > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END, 
                price_subtotal = CASE WHEN (price_subtotal > 10000 OR price_subtotal < -10000) AND price_subtotal != 0 THEN ROUND(price_subtotal / 1000000,2) ELSE CASE WHEN price_subtotal != 0 THEN  CASE WHEN price_subtotal > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                price_total = CASE WHEN (price_total > 10000 OR price_total < -10000) AND price_total != 0 THEN ROUND(price_total / 1000000,2) ELSE CASE WHEN price_total != 0 THEN  CASE WHEN price_total > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                amount_residual = CASE WHEN (amount_residual > 10000 OR amount_residual < -10000) AND amount_residual != 0 THEN ROUND(amount_residual / 1000000,2) ELSE CASE WHEN amount_residual != 0 THEN  CASE WHEN amount_residual > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                amount_currency = CASE WHEN (amount_currency > 10000 OR amount_currency < -10000) AND amount_currency != 0 THEN ROUND(amount_currency / 1000000,2) ELSE CASE WHEN amount_currency != 0 THEN  CASE WHEN amount_currency > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                tax_base_amount = CASE WHEN (tax_base_amount > 10000 OR tax_base_amount < -10000) AND tax_base_amount != 0 THEN ROUND(tax_base_amount / 1000000,2) ELSE CASE WHEN tax_base_amount != 0 THEN  CASE WHEN tax_base_amount > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                amount_residual_currency = CASE WHEN (tax_base_amount > 10000 OR tax_base_amount < -10000) AND tax_base_amount != 0 THEN ROUND(tax_base_amount / 1000000,2) ELSE CASE WHEN tax_base_amount != 0 THEN  CASE WHEN tax_base_amount > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """
                UPDATE account_move_line
                SET 
                debit = CASE WHEN (debit > 10000 OR debit < -10000) AND debit != 0 THEN ROUND(debit / 1000000,2) ELSE CASE WHEN debit != 0 THEN CASE WHEN debit > 0 AND debit != 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                credit = CASE WHEN (credit > 10000 OR credit < -10000) AND credit != 0 THEN ROUND(credit / 1000000,2) ELSE CASE WHEN credit != 0 THEN CASE WHEN credit > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                balance = CASE WHEN (balance > 10000 OR balance < -10000) AND balance != 0 THEN ROUND(balance / 1000000,2) ELSE CASE WHEN balance != 0 THEN  CASE WHEN balance > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END,
                amount_residual = CASE WHEN (amount_residual > 10000 OR amount_residual < -10000) AND amount_residual != 0 THEN ROUND(amount_residual / 1000000,2) ELSE CASE WHEN amount_residual != 0 THEN  CASE WHEN amount_residual > 0 THEN 0.01 ELSE -0.01 END ELSE 0.0 END END
                WHERE currency_id != 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_analytic_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_analytic_line
                SET 
                amount = CASE WHEN (amount > 10000 OR amount < -10000) AND amount != 0 THEN ROUND(amount /1000000,2) ELSE CASE WHEN amount != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_bank_statement');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_bank_statement
                SET
                balance_start = CASE WHEN (balance_start > 10000 OR balance_start < -10000) AND balance_start != 0 THEN ROUND(balance_start / 1000000,2) ELSE CASE WHEN balance_start != 0 THEN 0.01 ELSE 0.0 END END,
                balance_end_real = CASE WHEN (balance_end_real > 10000 OR balance_end_real < -10000) AND balance_end_real != 0 THEN ROUND(balance_end_real / 1000000,2) ELSE CASE WHEN balance_end_real != 0 THEN  0.01 ELSE 0.0 END END,
                total_entry_encoding = CASE WHEN (total_entry_encoding > 10000 OR total_entry_encoding < -10000) AND total_entry_encoding != 0 THEN ROUND(total_entry_encoding / 1000000,2) ELSE CASE WHEN total_entry_encoding != 0 THEN  0.01 ELSE 0.0 END END,
                balance_end = CASE WHEN (balance_end > 10000 OR balance_end < -10000) AND balance_end != 0 THEN ROUND(balance_end / 1000000,2) ELSE CASE WHEN balance_end != 0 THEN  0.01 ELSE 0.0 END END,
                difference = CASE WHEN (difference > 10000 OR difference < -10000) AND difference != 0 THEN ROUND(difference / 1000000,2) ELSE CASE WHEN difference != 0 THEN  0.01 ELSE 0.0 END END
                WHERE 
                journal_id IN 
                (
                SELECT aj.id FROM account_bank_statement AS accbs
                INNER JOIN account_journal AS aj ON aj.id = accbs.journal_id
                WHERE aj.currency_id = 3
                GROUP BY aj.id
                )
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_bank_statement_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_bank_statement_line
                SET
                amount = CASE WHEN (amount > 10000 OR amount < -10000) AND amount != 0 THEN ROUND(amount /1000000,2) ELSE CASE WHEN amount != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_partial_reconcile');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_partial_reconcile
                SET
                credit_amount_currency = CASE WHEN (credit_amount_currency > 10000 OR credit_amount_currency < -10000) AND credit_amount_currency != 0 THEN ROUND(credit_amount_currency /1000000,2) ELSE CASE WHEN credit_amount_currency != 0 THEN 0.01 ELSE 0.0 END END,
                debit_amount_currency = CASE WHEN (debit_amount_currency > 10000 OR debit_amount_currency < -10000) AND debit_amount_currency != 0 THEN ROUND(debit_amount_currency / 1000000,2) ELSE CASE WHEN debit_amount_currency != 0 THEN  0.01 ELSE 0.0 END END,
                amount = CASE WHEN (amount > 10000 OR amount < -10000) AND amount != 0 THEN ROUND(amount /1000000,2) ELSE CASE WHEN amount != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_payment');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_payment
                SET
                amount = CASE WHEN (amount > 10000 OR amount < -10000) AND amount != 0 THEN ROUND(amount /1000000,2) ELSE CASE WHEN amount != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_pays_islr');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """    
                UPDATE account_pays_islr
                SET
                amount = CASE WHEN (amount > 10000 OR amount < -10000) AND amount != 0 THEN ROUND(amount /1000000,2) ELSE CASE WHEN amount != 0 THEN 0.01 ELSE 0.0 END END 
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_asset');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """    
                UPDATE account_asset
                SET
                original_value = CASE WHEN (original_value > 10000 OR original_value < -10000) AND original_value != 0 THEN ROUND(original_value / 1000000,2) ELSE CASE WHEN original_value != 0 THEN  0.01 ELSE 0.0 END END,
                book_value = CASE WHEN (book_value > 10000 OR book_value < -10000) AND book_value != 0 THEN ROUND(book_value / 1000000,2) ELSE CASE WHEN book_value != 0 THEN  0.01 ELSE 0.0 END END,
                already_depreciated_amount_import = CASE WHEN (already_depreciated_amount_import > 10000 OR already_depreciated_amount_import < -10000) AND already_depreciated_amount_import != 0 THEN ROUND(already_depreciated_amount_import / 1000000,2) ELSE CASE WHEN already_depreciated_amount_import != 0 THEN  0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_wh_islr_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_wh_islr_line
                SET
                amount_invoice = CASE WHEN (amount_invoice > 10000 OR amount_invoice < -10000) AND amount_invoice != 0 THEN ROUND(amount_invoice /1000000,2) ELSE CASE WHEN amount_invoice != 0 THEN 0.01 ELSE 0.0 END END,
                base_tax = CASE WHEN (base_tax > 10000 OR base_tax < -10000) AND base_tax != 0 THEN ROUND(base_tax / 1000000,2) ELSE CASE WHEN base_tax != 0 THEN  0.01 ELSE 0.0 END END,
                ret_amount = CASE WHEN (ret_amount > 10000 OR ret_amount < -10000) AND ret_amount != 0 THEN ROUND(ret_amount / 1000000,2) ELSE CASE WHEN ret_amount != 0 THEN  0.01 ELSE 0.0 END END,
                sus_amount = CASE WHEN (sus_amount > 10000 OR sus_amount < -10000) AND sus_amount != 0 THEN ROUND(sus_amount / 1000000,2) ELSE CASE WHEN sus_amount != 0 THEN  0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_wh_iva_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_wh_iva_line
                SET
                amount_tax = CASE WHEN (amount_tax > 10000 OR amount_tax < -10000) AND amount_tax != 0 THEN ROUND(amount_tax /1000000,2) ELSE CASE WHEN amount_tax != 0 THEN 0.01 ELSE 0.0 END END,
                base_tax = CASE WHEN (base_tax > 10000 OR base_tax < -10000) AND base_tax != 0 THEN ROUND(base_tax / 1000000,2) ELSE CASE WHEN base_tax != 0 THEN  0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_wh_iva_pay');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_wh_iva_pay
                SET
                amount = CASE WHEN (amount > 10000 OROR amount < -10000) AND amount != 0 THEN ROUND(amount /1000000,2) ELSE CASE WHEN amount != 0 THEN 0.01 ELSE 0.0 END END
                """

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_withholding_rate_table');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_withholding_rate_table
                SET
                parcentage_subtracting_1 = CASE WHEN (parcentage_subtracting_1::numeric > 10000  OR parcentage_subtracting_1::numeric < -10000) AND parcentage_subtracting_1::numeric != 0 THEN ROUND(parcentage_subtracting_1::numeric / 1000000,2) ELSE CASE WHEN parcentage_subtracting_1::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                parcentage_subtracting_3 = CASE WHEN (parcentage_subtracting_3::numeric > 10000  OR parcentage_subtracting_3::numeric < -10000) AND parcentage_subtracting_3::numeric != 0 THEN ROUND(parcentage_subtracting_3::numeric / 1000000,2) ELSE CASE WHEN parcentage_subtracting_3::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount = CASE WHEN (amount::numeric > 10000  OR amount::numeric < -10000) AND amount::numeric != 0 THEN ROUND(amount::numeric /1000000,2) ELSE CASE WHEN amount::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'account_withholding_rate_table_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE account_withholding_rate_table_line 
                SET
                apply_up_to = CASE WHEN (apply_up_to::numeric > 10000 OR apply_up_to::numeric < -10000) AND apply_up_to::numeric != 0 THEN ROUND(apply_up_to::numeric /1000000,2) ELSE CASE WHEN apply_up_to::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'crm_lead');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE crm_lead
                SET
                recurring_revenue = CASE WHEN (recurring_revenue > 10000 OR recurring_revenue < -10000) AND recurring_revenue != 0 THEN ROUND(recurring_revenue /1000000,2) ELSE CASE WHEN recurring_revenue != 0 THEN 0.01 ELSE 0.0 END END,
                expected_revenue = CASE WHEN (expected_revenue > 10000 OR expected_revenue < -10000) AND expected_revenue != 0 THEN ROUND(expected_revenue / 1000000,2) ELSE CASE WHEN expected_revenue != 0 THEN  0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'mrp_workcenter');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE mrp_workcenter
                SET
                costs_hour = CASE WHEN (costs_hour::numeric > 10000 OR costs_hour::numeric < -10000) AND costs_hour::numeric != 0 THEN ROUND(costs_hour::numeric / 1000000,2) ELSE CASE WHEN costs_hour::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'municipality_tax');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE municipality_tax
                SET
                amount = CASE WHEN (amount::numeric > 10000 OR amount::numeric < -10000) AND amount::numeric != 0 THEN ROUND(amount::numeric / 1000000,2) ELSE CASE WHEN amount::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                withheld_amount = CASE WHEN (withheld_amount::numeric > 10000 OR withheld_amount::numeric < -10000) AND withheld_amount::numeric != 0 THEN ROUND(withheld_amount::numeric / 1000000,2) ELSE CASE WHEN withheld_amount::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'municipality_tax_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE municipality_tax_line
                SET
                wh_amount = CASE WHEN (wh_amount::numeric > 10000 OR wh_amount::numeric < -10000) AND wh_amount::numeric != 0 THEN ROUND(wh_amount::numeric / 1000000,2) ELSE CASE WHEN wh_amount::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'product_attribute_custom_value');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE product_attribute_custom_value
                SET
                custom_value = CASE WHEN (custom_value::numeric > 10000 OR custom_value::numeric < -10000) AND custom_value::numeric != 0 THEN ROUND(custom_value::numeric /1000000,2) ELSE CASE WHEN custom_value::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'product_supplierinfo');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE product_supplierinfo
                SET
                price = CASE WHEN (price > 10000 OR price < -10000) AND price != 0 THEN ROUND(price /1000000,2) ELSE CASE WHEN price != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'product_template');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE product_template
                SET
                list_price = CASE WHEN (list_price > 10000 OR list_price < -10000) AND list_price != 0 THEN ROUND(list_price /1000000,2) ELSE CASE WHEN list_price != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'purchase_order');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE purchase_order
                SET
                amount_untaxed = CASE WHEN (amount_untaxed > 10000 OR amount_untaxed < -10000) AND amount_untaxed != 0 THEN ROUND(amount_untaxed /1000000,2) ELSE CASE WHEN amount_untaxed != 0 THEN 0.01 ELSE 0.0 END END,
                amount_tax = CASE WHEN (amount_tax > 10000 OR amount_tax < -10000) AND amount_tax != 0 THEN ROUND(amount_tax / 1000000,2) ELSE CASE WHEN amount_tax != 0 THEN  0.01 ELSE 0.0 END END,
                amount_total = CASE WHEN (amount_total > 10000 OR amount_total < -10000) AND amount_total != 0 THEN ROUND(amount_total / 1000000,2) ELSE CASE WHEN amount_total != 0 THEN  0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'purchase_order_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE purchase_order_line
                SET
                price_unit = CASE WHEN (price_unit > 10000 OR price_unit < -10000) AND price_unit != 0 THEN ROUND(price_unit /1000000,2) ELSE CASE WHEN price_unit != 0 THEN 0.01 ELSE 0.0 END END,
                price_subtotal = CASE WHEN (price_subtotal > 10000 OR price_subtotal < -10000) AND price_subtotal != 0 THEN ROUND(price_subtotal / 1000000,2) ELSE CASE WHEN price_subtotal != 0 THEN  0.01 ELSE 0.0 END END,
                price_total =  CASE WHEN (price_total > 10000 OR price_total < -10000) AND price_total != 0 THEN ROUND(price_total / 1000000,2) ELSE CASE WHEN price_total != 0 THEN  0.01 ELSE 0.0 END END,
                price_tax =  CASE WHEN (price_tax::numeric > 10000 OR price_tax::numeric < -10000) AND price_tax::numeric != 0 THEN ROUND(price_tax::numeric / 1000000,2) ELSE CASE WHEN price_tax::numeric != 0 THEN  0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'purchase_requistion_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE purchase_requistion_line
                SET
                price_unit = CASE WHEN (price_unit > 10000 OR price_unit < -10000) AND price_unit != 0 THEN ROUND(price_unit /1000000,2) ELSE CASE WHEN price_unit != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'res_currency_rate');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE res_currency_rate
                SET
                rate = rate::numeric * 1000000
                WHERE currency_id != 3 AND rate != 0
                """
                self._cr.execute(sql)
                
            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'sale_order');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE sale_order
                SET
                amount_untaxed = CASE WHEN (amount_untaxed > 10000 OR amount_untaxed < -10000) AND amount_untaxed != 0 THEN ROUND(amount_untaxed /1000000,2) ELSE CASE WHEN amount_untaxed != 0 THEN 0.01 ELSE 0.0 END END,
                amount_tax = CASE WHEN (amount_tax > 10000 OR amount_tax < -10000) AND amount_tax != 0 THEN ROUND(amount_tax / 1000000,2) ELSE CASE WHEN amount_tax != 0 THEN 0.01 ELSE 0.0 END END,
                amount_total = CASE WHEN (amount_total > 10000 OR amount_total < -10000) AND amount_total != 0 THEN ROUND(amount_total / 1000000,2) ELSE CASE WHEN amount_total != 0 THEN  0.01 ELSE 0.0 END END,
                margin = CASE WHEN (margin > 10000 OR margin < -10000) AND margin != 0 THEN ROUND(margin / 1000000,2) ELSE CASE WHEN margin != 0 THEN  0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'sale_order_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE sale_order_line
                SET
                price_unit  = CASE WHEN (price_unit > 10000 OR price_unit < -10000) AND price_unit != 0 THEN ROUND(price_unit /1000000,2) ELSE CASE WHEN price_unit != 0 THEN 0.011 ELSE 0.0 END END,
                price_subtotal = CASE WHEN (price_subtotal > 10000 OR price_subtotal < -10000) AND price_subtotal != 0 THEN ROUND(price_subtotal / 1000000,2) ELSE CASE WHEN price_subtotal != 0 THEN  0.01 ELSE 0.0 END END,
                price_tax = CASE WHEN (price_tax::numeric > 10000 OR price_tax::numeric < -10000) AND price_tax::numeric != 0 THEN ROUND(price_tax::numeric / 1000000,2) ELSE CASE WHEN price_tax::numeric != 0 THEN  0.01 ELSE 0.0 END END,
                price_reduce = CASE WHEN (price_reduce > 10000 OR price_reduce < -10000) AND price_reduce != 0 THEN ROUND(price_reduce / 1000000,2) ELSE CASE WHEN price_reduce != 0 THEN  0.01 ELSE 0.0 END END,
                price_reduce_taxinc =  CASE WHEN (price_reduce_taxinc > 10000 OR price_reduce_taxinc < -10000) AND price_reduce_taxinc != 0 THEN ROUND(price_reduce_taxinc /  1000000,2) ELSE CASE WHEN price_reduce_taxinc != 0 THEN  0.01 ELSE 0.0 END END,
                price_reduce_taxexcl = CASE WHEN (price_reduce_taxexcl > 10000 OR price_reduce_taxexcl < -10000) AND price_reduce_taxexcl != 0 THEN ROUND(price_reduce_taxexcl / 1000000,2) ELSE CASE WHEN price_reduce_taxexcl != 0 THEN  0.01 ELSE 0.0 END END,
                untaxed_amount_to_invoice = CASE WHEN (untaxed_amount_to_invoice > 10000 OR untaxed_amount_to_invoice < -10000) AND untaxed_amount_to_invoice != 0 THEN ROUND(untaxed_amount_to_invoice / 1000000,2) ELSE CASE WHEN untaxed_amount_to_invoice != 0 THEN  0.01 ELSE 0.0 END END,
                margin = CASE WHEN (margin > 10000 OR margin < -10000) AND margin != 0 THEN ROUND(margin / 1000000,2) ELSE CASE WHEN margin != 0 THEN  0.01 ELSE 0.0 END END,
                purchase_price =  CASE WHEN (purchase_price > 10000 OR purchase_price < -10000) AND purchase_price != 0 THEN ROUND(purchase_price / 1000000,2) ELSE CASE WHEN purchase_price != 0 THEN  0.01 ELSE 0.0 END END,
                price_total =  CASE WHEN (price_total > 10000 OR price_total < -10000) AND price_total != 0 THEN ROUND(price_total / 1000000,2) ELSE CASE WHEN price_total != 0 THEN  0.01 ELSE 0.0 END END,
                untaxed_amount_invoiced =  CASE WHEN (untaxed_amount_invoiced > 10000 OR untaxed_amount_invoiced < -10000) AND untaxed_amount_invoiced != 0 THEN ROUND(untaxed_amount_invoiced / 1000000,2) ELSE CASE WHEN untaxed_amount_invoiced != 0 THEN  0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)




            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'stock_landed_cost');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE stock_landed_cost
                SET
                amount_total = CASE WHEN (amount_total::numeric > 10000 OR amount_total::numeric < -10000) AND amount_total::numeric != 0 THEN ROUND(amount_total::numeric /1000000,2) ELSE CASE WHEN amount_total::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'stock_landed_cost_lines');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE stock_landed_cost_lines
                SET
                price_unit = CASE WHEN (price_unit::numeric > 10000 OR price_unit::numeric < -10000) AND price_unit::numeric != 0 THEN ROUND(price_unit::numeric /1000000,2) ELSE CASE WHEN price_unit::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'stock_move');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE stock_move
                SET
                price_unit = CASE WHEN (price_unit::numeric > 10000 OR price_unit::numeric < -10000) AND price_unit::numeric != 0 THEN ROUND(price_unit::numeric /1000000,2) ELSE CASE WHEN price_unit::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'stock_valuation_layer');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE stock_valuation_layer
                SET
                unit_cost = CASE WHEN (unit_cost > 10000 OR unit_cost < -10000) AND unit_cost != 0 THEN ROUND(unit_cost /1000000,2) ELSE CASE WHEN unit_cost != 0 THEN 0.01 ELSE 0.0 END END,
                value = CASE WHEN (value > 10000 OR value < -10000) AND value != 0 THEN ROUND(value / 1000000,2) ELSE CASE WHEN value != 0 THEN  0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'tax_municipal_declaration');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE tax_municipal_declaration
                SET
                total_retenido = CASE WHEN (total_retenido::numeric > 10000 OR total_retenido::numeric < -10000) AND total_retenido::numeric != 0 THEN ROUND(total_retenido::numeric /1000000,2) ELSE CASE WHEN total_retenido::numeric != 0 THEN 0.01 ELSE 0.0 END END 
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'tax_municipal_declaration_line');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE tax_municipal_declaration_line
                SET
                base_imponible = CASE WHEN (base_imponible::numeric > 10000 OR base_imponible::numeric < -10000) AND base_imponible::numeric != 0 THEN ROUND(base_imponible::numeric /1000000,2) ELSE CASE WHEN base_imponible::numeric != 0 THEN 0.01 ELSE 0.0 END END, 
                amount_total_invoice = CASE WHEN (amount_total_invoice::numeric > 10000 OR amount_total_invoice::numeric < -10000) AND amount_total_invoice::numeric != 0 THEN ROUND(amount_total_invoice::numeric /1000000,2) ELSE CASE WHEN amount_total_invoice::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_total_ret = CASE WHEN (amount_total_ret::numeric > 10000 OR amount_total_ret::numeric < -10000) AND amount_total_ret::numeric != 0 THEN ROUND(amount_total_ret::numeric /1000000,2) ELSE CASE WHEN amount_total_ret::numeric != 0 THEN 0.01 ELSE 0.0 END END 
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'tributary_unit');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE tributary_unit
                SET
                amount = CASE WHEN (amount::numeric > 10000 OR amount::numeric < -10000) AND amount::numeric != 0 THEN ROUND(amount::numeric /1000000,2) ELSE CASE WHEN amount::numeric != 0 THEN 0.01 ELSE 0.0 END END 
                """
                self._cr.execute(sql)

            sql = """SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND   table_name = 'ir_property');"""
            self._cr.execute(sql)
            res = self._cr.dictfetchall()
            res = res and res[0] or {}
            if res.get('exists', False):
                sql = """
                UPDATE ir_property
                SET
                value_float = CASE WHEN (value_float::numeric > 10000 OR value_float::numeric < -10000) AND value_float::numeric != 0 THEN ROUND(value_float::numeric /1000000,2) ELSE CASE WHEN value_float::numeric != 0 THEN 0.01 ELSE 0.0 END END
                WHERE type = 'float' and name = 'standard_price'
                """
                self._cr.execute(sql)

             # Modulos Personalizados
            instalado = True if self.env['ir.module.module'].search([('name','=','eu_multi_currency'),('state','=','installed')]) else False
            if instalado:
                ### INICIO FACTURAS ###
                sql = """
                UPDATE account_move
                SET
                tasa_del_dia_two = CASE WHEN (tasa_del_dia_two::numeric > 10000 OR tasa_del_dia_two::numeric < -10000) AND tasa_del_dia_two::numeric != 0 THEN ROUND(tasa_del_dia_two::numeric /1000000,2) ELSE CASE WHEN tasa_del_dia_two::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = manual_currency_exchange_rate::numeric * 1000000,
                tasa_del_dia = tasa_del_dia::numeric * 1000000
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """
                UPDATE account_move
                SET
                tasa_del_dia = CASE WHEN (tasa_del_dia::numeric > 10000 OR tasa_del_dia::numeric < -10000) AND tasa_del_dia::numeric != 0 THEN ROUND(tasa_del_dia::numeric /1000000,2) ELSE CASE WHEN tasa_del_dia::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_ref = CASE WHEN (amount_ref::numeric > 10000 OR amount_ref::numeric < -10000) AND amount_ref::numeric != 0 THEN ROUND(amount_ref::numeric /1000000,2) ELSE CASE WHEN amount_ref::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = CASE WHEN (manual_currency_exchange_rate::numeric > 10000 OR manual_currency_exchange_rate::numeric < -10000) AND manual_currency_exchange_rate::numeric != 0 THEN ROUND(manual_currency_exchange_rate::numeric /1000000,2) ELSE CASE WHEN manual_currency_exchange_rate::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                tasa_del_dia_two = tasa_del_dia_two::numeric * 1000000
                WHERE currency_id != 3
                """
                self._cr.execute(sql)
                ### FIN FACTURAS ###

                ### INICIO PAGOS ###
                sql = """ 
                UPDATE account_payment
                SET
                tasa_del_dia_two = CASE WHEN (tasa_del_dia_two::numeric > 10000 OR tasa_del_dia_two::numeric < -10000) AND tasa_del_dia_two::numeric != 0 THEN ROUND(tasa_del_dia_two::numeric /1000000,2) ELSE CASE WHEN tasa_del_dia_two::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = manual_currency_exchange_rate::numeric * 1000000,
                tasa_del_dia = tasa_del_dia::numeric * 1000000
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """ 
                UPDATE account_payment
                SET
                tasa_del_dia = CASE WHEN (tasa_del_dia::numeric > 10000 OR tasa_del_dia::numeric < -10000) AND tasa_del_dia::numeric != 0 THEN ROUND(tasa_del_dia::numeric /1000000,2) ELSE CASE WHEN tasa_del_dia::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_ref = CASE WHEN (amount_ref::numeric > 10000 OR amount_ref::numeric < -10000) AND amount_ref::numeric != 0 THEN ROUND(amount_ref::numeric /1000000,2) ELSE CASE WHEN amount_ref::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = CASE WHEN (manual_currency_exchange_rate::numeric > 10000 OR manual_currency_exchange_rate::numeric < -10000) AND manual_currency_exchange_rate::numeric != 0 THEN ROUND(manual_currency_exchange_rate::numeric /1000000,2) ELSE CASE WHEN manual_currency_exchange_rate::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                tasa_del_dia_two = tasa_del_dia_two::numeric * 1000000
                WHERE currency_id != 3
                """
                self._cr.execute(sql)

                ### FIN PAGOS ###

                ### INICIO ORDEN DE COMPRA
                sql = """ 
                UPDATE purchase_order
                SET
                tax_today_two = CASE WHEN (tax_today_two::numeric > 10000 OR tax_today_two::numeric < -10000) AND tax_today_two::numeric != 0 THEN ROUND(tax_today_two::numeric /1000000,2) ELSE CASE WHEN tax_today_two::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = manual_currency_exchange_rate::numeric * 1000000,
                tax_today = tax_today::numeric * 1000000
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """ 
                UPDATE purchase_order
                SET
                tax_today = CASE WHEN (tax_today::numeric > 10000 OR tax_today::numeric < -10000) AND tax_today::numeric != 0 THEN ROUND(tax_today::numeric /1000000,2) ELSE CASE WHEN tax_today::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_total_ref = CASE WHEN (amount_total_ref::numeric > 10000 OR amount_total_ref::numeric < -10000) AND amount_total_ref::numeric != 0 THEN ROUND(amount_total_ref::numeric /1000000,2) ELSE CASE WHEN amount_total_ref::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                tax_today_two = tax_today_two::numeric * 1000000,
                manual_currency_exchange_rate = CASE WHEN (manual_currency_exchange_rate::numeric > 10000 OR manual_currency_exchange_rate::numeric < -10000) AND manual_currency_exchange_rate::numeric != 0 THEN ROUND(manual_currency_exchange_rate::numeric /1000000,2) ELSE CASE WHEN manual_currency_exchange_rate::numeric != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id != 3
                """
                self._cr.execute(sql)
                ### FIN ORDEN DE COMPRA

                ### INICIO ORDEN DE VENTAS
                sql = """ 
                UPDATE sale_order
                SET
                tax_today_two = CASE WHEN (tax_today_two::numeric > 10000 OR tax_today_two::numeric < -10000) AND tax_today_two::numeric != 0 THEN ROUND(tax_today_two::numeric /1000000,2) ELSE CASE WHEN tax_today_two::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = manual_currency_exchange_rate::numeric * 1000000,
                tax_today = tax_today::numeric * 1000000
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """ 
                UPDATE sale_order
                SET
                tax_today = CASE WHEN (tax_today::numeric > 10000 OR tax_today::numeric < -10000) AND tax_today::numeric != 0 THEN ROUND(tax_today::numeric /1000000,2) ELSE CASE WHEN tax_today::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_total_ref = CASE WHEN (amount_total_ref::numeric > 10000 OR amount_total_ref::numeric < -10000) AND amount_total_ref::numeric != 0 THEN ROUND(amount_total_ref::numeric /1000000,2) ELSE CASE WHEN amount_total_ref::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                tax_today_two = tax_today_two::numeric * 1000000,
                manual_currency_exchange_rate = CASE WHEN (manual_currency_exchange_rate::numeric > 10000 OR manual_currency_exchange_rate::numeric < -10000) AND manual_currency_exchange_rate::numeric != 0 THEN ROUND(manual_currency_exchange_rate::numeric /1000000,2) ELSE CASE WHEN manual_currency_exchange_rate::numeric != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id != 3
                """
                self._cr.execute(sql)
                ### FIN ORDEN DE VENTAS
            
            instalado = True if self.env['ir.module.module'].search([('name','=','eu_usd_product'),('state','=','installed')]) else False
            if instalado:
                ### INICIO PRODUCTOS
                sql = """ 
                UPDATE product_template
                SET
                tax_today = CASE WHEN (tax_today::numeric > 10000 OR tax_today::numeric < -10000) AND tax_today::numeric != 0 THEN ROUND(tax_today::numeric /1000000,2) ELSE CASE WHEN tax_today::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)
                ### FIN PRODUCTOS

            instalado = True if self.env['ir.module.module'].search([('name','=','l10n_ve_retencion_islr'),('state','=','installed')]) else False
            if instalado:
                ### INICIO RETENCION ISLR ###
                sql = """
                UPDATE account_move
                SET
                amount_wh_islr = CASE WHEN (amount_wh_islr::numeric > 10000 OR amount_wh_islr::numeric < -10000) AND amount_wh_islr::numeric != 0 THEN ROUND(amount_wh_islr::numeric /1000000,2) ELSE CASE WHEN amount_wh_islr::numeric != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)
                ### FIN RETENCION ISLR ###

            instalado = True if self.env['ir.module.module'].search([('name','=','l10n_ve_retencion_iva'),('state','=','installed')]) else False
            if instalado:
                ### INICIO RETENCION ISLR ###
                sql = """
                UPDATE account_move
                SET
                amount_wh_iva = CASE WHEN (amount_wh_iva::numeric > 10000 OR amount_wh_iva::numeric < -10000) AND amount_wh_iva::numeric != 0 THEN ROUND(amount_wh_iva::numeric /1000000,2) ELSE CASE WHEN amount_wh_iva::numeric != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id = 3
                """
                self._cr.execute(sql)
                ### FIN RETENCION ISLR ###

            instalado = True if self.env['ir.module.module'].search([('name','=','intercompany_transaction_ept'),('state','=','installed')]) else False
            if instalado:
                ### INICIO Inter Company Transfer ###
                sql = """
                UPDATE inter_company_transfer_line_ept
                SET
                price = CASE WHEN (price::numeric > 10000 OR price::numeric < -10000) AND price::numeric != 0 THEN ROUND(price::numeric /1000000,2) ELSE CASE WHEN price::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)
                ### FIN Inter Company Transfer ###

            instalado = True if self.env['ir.module.module'].search([('name','=','locv_account_advance_payment'),('state','=','installed')]) else False
            if instalado:
                ### INICIO Anticipos ###
                sql = """
                UPDATE account_advanced_payment
                SET
                amount_advance = CASE WHEN (amount_advance::numeric > 10000 OR amount_advance::numeric < -10000) AND amount_advance::numeric != 0 THEN ROUND(amount_advance::numeric /1000000,2) ELSE CASE WHEN amount_advance::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_apply = CASE WHEN (amount_apply::numeric > 10000 OR amount_apply::numeric < -10000) AND amount_apply::numeric != 0 THEN ROUND(amount_apply::numeric /1000000,2) ELSE CASE WHEN amount_apply::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_apply_conversion = CASE WHEN (amount_apply_conversion::numeric > 10000 OR amount_apply_conversion::numeric < -10000) AND amount_apply_conversion::numeric != 0 THEN ROUND(amount_apply_conversion::numeric /1000000,2) ELSE CASE WHEN amount_apply_conversion::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                amount_invoice_in_company = CASE WHEN (amount_invoice_in_company::numeric > 10000 OR amount_invoice_in_company::numeric < -10000) AND amount_invoice_in_company::numeric != 0 THEN ROUND(amount_invoice_in_company::numeric /1000000,2) ELSE CASE WHEN amount_invoice_in_company::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = manual_currency_exchange_rate::numeric * 1000000
                WHERE currency_id = 3
                """
                self._cr.execute(sql)

                sql = """
                UPDATE account_advanced_payment
                SET
                amount_advance = CASE WHEN (amount_advance::numeric > 10000 OR amount_advance::numeric < -10000) AND amount_advance::numeric != 0 THEN ROUND(amount_advance::numeric /1000000,2) ELSE CASE WHEN amount_advance::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                manual_currency_exchange_rate = CASE WHEN (manual_currency_exchange_rate::numeric > 10000 OR manual_currency_exchange_rate::numeric < -10000) AND manual_currency_exchange_rate::numeric != 0 THEN ROUND(manual_currency_exchange_rate::numeric /1000000,2) ELSE CASE WHEN manual_currency_exchange_rate::numeric != 0 THEN 0.01 ELSE 0.0 END END
                WHERE currency_id != 3
                """
                self._cr.execute(sql)
                ### FIN Anticipos ###
            
            instalado = True if self.env['ir.module.module'].search([('name','=','sh_po_tender_management'),('state','=','installed')]) else False
            if instalado:
                ### INICIO Acuerdos de Compra ###
                sql = """
                UPDATE purchase_agreement_line
                SET
                sh_price_unit = CASE WHEN (sh_price_unit::numeric > 10000 OR sh_price_unit::numeric < -10000) AND sh_price_unit::numeric != 0 THEN ROUND(sh_price_unit::numeric /1000000,2) ELSE CASE WHEN sh_price_unit::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)
                ### FIN Acuerdos de Compra ###

            instalado = True if self.env['ir.module.module'].search([('name','=','account_consolidation'),('state','=','installed')]) else False
            if instalado:
                ### INICIO Consolidación  ###
                sql = """
                UPDATE consolidation_company_period
                SET
                currency_rate_avg = CASE WHEN (currency_rate_avg::numeric > 10000 OR currency_rate_avg::numeric < -10000) AND currency_rate_avg::numeric != 0 THEN ROUND(currency_rate_avg::numeric /1000000,2) ELSE CASE WHEN currency_rate_avg::numeric != 0 THEN 0.01 ELSE 0.0 END END,
                currency_rate_end = CASE WHEN (currency_rate_end::numeric > 10000 OR currency_rate_end::numeric < -10000) AND currency_rate_end::numeric != 0 THEN ROUND(currency_rate_end::numeric /1000000,2) ELSE CASE WHEN currency_rate_end::numeric != 0 THEN 0.01 ELSE 0.0 END END
                """
                self._cr.execute(sql)
                ### FIN Consolidación  ###

            