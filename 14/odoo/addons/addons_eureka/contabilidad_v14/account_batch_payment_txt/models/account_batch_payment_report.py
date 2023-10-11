# -*- coding: utf-8 -*-

from odoo import api, models

PAY_LINES_PER_PAGE = 28


class PrintBatchPayment(models.AbstractModel):
    _name = 'report.account_batch_payment_txt.print_batch_payment_custom'
    _template = 'account_batch_payment.print_batch_payment_custom'
    _description = 'Batch Deposit Report'

    def get_pages(self, batch):
        """ Returns the data structure used by the template
        """
        i = 0
        payment_slices = []
        while i < len(batch.payment_ids):
            payment_slices.append(batch.payment_ids[i:i+PAY_LINES_PER_PAGE])
            i += PAY_LINES_PER_PAGE

        return [{
            'date': batch.date,
            'batch_name': batch.name,
            'journal_name': batch.journal_id.name,
            'payments': payments,
            'acc_number': batch.acc_number.acc_number,
            'acc_number_bank_id': batch.acc_number.bank_id.name,
            'company':self.env.company.name,
            'logo':self.env.company.logo,
            # 'centro_costo' : batch.analytic_account_id.display_name,
            'currency': batch.currency_id,
            'payment_method_id': batch.payment_method_id.name,
            'name': batch.name,
            'total_amount': batch.amount if idx == len(payment_slices) - 1 else 0,
            'footer': batch.journal_id.company_id.report_footer,
        } for idx, payments in enumerate(payment_slices)]

    @api.model
    def _get_report_values(self, docids, data=None):
        report_name = 'account_batch_payment_txt.print_batch_payment_custom'
        report = self.env['ir.actions.report']._get_report_from_name(report_name)
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'pages': self.get_pages,
        }
