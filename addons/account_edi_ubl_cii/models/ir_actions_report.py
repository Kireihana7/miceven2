# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.tools import cleanup_xml_node
<<<<<<< HEAD
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

from lxml import etree
import base64
from xml.sax.saxutils import escape, quoteattr
<<<<<<< HEAD
import io
=======
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

<<<<<<< HEAD
    def _add_pdf_into_invoice_xml(self, invoice, stream_data):
        format_codes = ['ubl_bis3', 'ubl_de', 'nlcius_1', 'efff_1']
        edi_attachments = invoice.edi_document_ids.filtered(lambda d: d.edi_format_id.code in format_codes).sudo().attachment_id
        for edi_attachment in edi_attachments:
            old_xml = base64.b64decode(edi_attachment.with_context(bin_size=False).datas, validate=True)
            tree = etree.fromstring(old_xml)
            anchor_elements = tree.xpath("//*[local-name()='AccountingSupplierParty']")
            additional_document_elements = tree.xpath("//*[local-name()='AdditionalDocumentReference']")
            # with this clause, we ensure the xml are only postprocessed once (even when the invoice is reset to
            # draft then validated again)
            if anchor_elements and not additional_document_elements:
                pdf_stream = stream_data['stream']
                pdf_content_b64 = base64.b64encode(pdf_stream.getvalue()).decode()
                pdf_name = '%s.pdf' % invoice.name.replace('/', '_')
                to_inject = '''
                    <cac:AdditionalDocumentReference
                        xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
                        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                        <cbc:ID>%s</cbc:ID>
                        <cac:Attachment>
                            <cbc:EmbeddedDocumentBinaryObject mimeCode="application/pdf" filename=%s>
                                %s
                            </cbc:EmbeddedDocumentBinaryObject>
                        </cac:Attachment>
                    </cac:AdditionalDocumentReference>
                ''' % (escape(pdf_name), quoteattr(pdf_name), pdf_content_b64)

                anchor_index = tree.index(anchor_elements[0])
                tree.insert(anchor_index, etree.fromstring(to_inject))
                new_xml = etree.tostring(cleanup_xml_node(tree), xml_declaration=True, encoding='UTF-8')
                edi_attachment.sudo().write({
                    'res_model': 'account.move',
                    'res_id': invoice.id,
                    'datas': base64.b64encode(new_xml),
                    'mimetype': 'application/xml',
                })

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        # EXTENDS base
        # Add the pdf report in the XML as base64 string.
        collected_streams = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)

        if collected_streams \
                and res_ids \
                and self._get_report(report_ref).report_name in ('account.report_invoice_with_payments', 'account.report_invoice'):
            for res_id, stream_data in collected_streams.items():
                invoice = self.env['account.move'].browse(res_id)
                self._add_pdf_into_invoice_xml(invoice, stream_data)

            # If Factur-X isn't already generated, generate and embed it inside the PDF
            if len(res_ids) == 1:
                invoice = self.env['account.move'].browse(res_ids)
                edi_doc_codes = invoice.edi_document_ids.edi_format_id.mapped('code')
                # If Factur-X hasn't been generated, generate and embed it anyway
                if invoice.is_sale_document() \
                        and invoice.state == 'posted' \
                        and 'facturx_1_0_05' not in edi_doc_codes \
                        and self.env.ref('account_edi_ubl_cii.edi_facturx_1_0_05', raise_if_not_found=False):
                    # Add the attachments to the pdf file
                    pdf_stream = collected_streams[invoice.id]['stream']

                    # Read pdf content.
                    pdf_content = pdf_stream.getvalue()
                    reader_buffer = io.BytesIO(pdf_content)
                    reader = OdooPdfFileReader(reader_buffer, strict=False)

                    # Post-process and embed the additional files.
                    writer = OdooPdfFileWriter()
                    writer.cloneReaderDocumentRoot(reader)

                    # Generate and embed Factur-X
                    xml_content, _errors = self.env['account.edi.xml.cii']._export_invoice(invoice)
                    writer.addAttachment(
                        name=self.env['account.edi.xml.cii']._export_invoice_filename(invoice),
                        data=xml_content,
                        subtype='text/xml',
                    )

                    # Replace the current content.
                    pdf_stream.close()
                    new_pdf_stream = io.BytesIO()
                    writer.write(new_pdf_stream)
                    collected_streams[invoice.id]['stream'] = new_pdf_stream

        return collected_streams
=======
    def _postprocess_pdf_report(self, record, buffer):
        """
        EXTENDS account
        Add the pdf report in XML as base64 string.
        """
        result = super()._postprocess_pdf_report(record, buffer)

        if record._name == 'account.move':
            # exclude efff because it's handled by l10n_be_edi
            format_codes = ['ubl_bis3', 'ubl_de', 'nlcius_1']
            edi_attachments = record.edi_document_ids.filtered(lambda d: d.edi_format_id.code in format_codes).attachment_id
            for edi_attachment in edi_attachments:
                old_xml = base64.b64decode(edi_attachment.with_context(bin_size=False).datas, validate=True)
                tree = etree.fromstring(old_xml)
                anchor_elements = tree.xpath("//*[local-name()='AccountingSupplierParty']")
                additional_document_elements = tree.xpath("//*[local-name()='AdditionalDocumentReference']")
                # with this clause, we ensure the xml are only postprocessed once (even when the invoice is reset to
                # draft then validated again)
                if anchor_elements and not additional_document_elements:
                    pdf = base64.b64encode(buffer.getvalue()).decode()
                    pdf_name = '%s.pdf' % record.name.replace('/', '_')
                    to_inject = '''
                        <cac:AdditionalDocumentReference
                            xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
                            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                            <cbc:ID>%s</cbc:ID>
                            <cac:Attachment>
                                <cbc:EmbeddedDocumentBinaryObject mimeCode="application/pdf" filename=%s>
                                    %s
                                </cbc:EmbeddedDocumentBinaryObject>
                            </cac:Attachment>
                        </cac:AdditionalDocumentReference>
                    ''' % (escape(pdf_name), quoteattr(pdf_name), pdf)

                    anchor_index = tree.index(anchor_elements[0])
                    tree.insert(anchor_index, etree.fromstring(to_inject))
                    new_xml = etree.tostring(cleanup_xml_node(tree), xml_declaration=True, encoding='UTF-8')
                    edi_attachment.write({
                        'res_model': 'account.move',
                        'res_id': record.id,
                        'datas': base64.b64encode(new_xml),
                        'mimetype': 'application/xml',
                    })

        return result
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
