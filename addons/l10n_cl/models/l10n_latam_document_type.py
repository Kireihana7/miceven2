# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class L10nLatamDocumentType(models.Model):

    _inherit = 'l10n_latam.document.type'

    internal_type = fields.Selection(
        selection_add=[
            ('invoice', 'Invoices'),
            ('invoice_in', 'Purchase Invoices'),
            ('debit_note', 'Debit Notes'),
            ('credit_note', 'Credit Notes'),
            ('receipt_invoice', 'Receipt Invoice'),
            ('stock_picking', 'Stock Delivery'),
        ],
    )
    l10n_cl_active = fields.Boolean(
        'Active in localization', help='This boolean enables document to be included on invoicing')

    def _format_document_number(self, document_number):
        """ Make validation of Import Dispatch Number
          * making validations on the document_number. If it is wrong it should raise an exception
          * format the document_number against a pattern and return it
        """
        self.ensure_one()
        if self.country_id.code != "CL":
            return super()._format_document_number(document_number)

        if not document_number:
            return False

        return document_number.zfill(6)

<<<<<<< HEAD
    def _is_doc_type_vendor(self):
        return self.code == '46'
=======
    def _filter_taxes_included(self, taxes):
        """ In Chile we include taxes depending on document type """
        self.ensure_one()
        if self.country_id.code == "CL" and self.code in ['39', '41', '110', '111', '112', '34']:
            return taxes.filtered(lambda x: x.l10n_cl_sii_code == 14)
        return super()._filter_taxes_included(taxes)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
